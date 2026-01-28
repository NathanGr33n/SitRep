"""
Event processing pipeline.
Orchestrates NLP, geocoding, and event construction.
"""
import logging
import hashlib
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.models.event import Event
from app.services.nlp_service import nlp_service
from app.services.geocoding_service import geocoding_service
from app.config import settings

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Processes raw content into structured security events.
    Handles the full pipeline: text → NLP → geocoding → database.
    """
    
    def __init__(self):
        self.nlp = nlp_service
        self.geocoder = geocoding_service
        
    def process_article(
        self,
        title: str,
        content: str,
        source_url: str,
        published_date: datetime,
        source_type: str = "news",
        source_reliability: float = 0.5,
        db: Optional[Session] = None
    ) -> Optional[Event]:
        """
        Process a raw article into a security event.
        
        Args:
            title: Article title
            content: Full article text
            source_url: Source URL
            published_date: Publication date
            source_type: Type of source (news, government, social, etc.)
            source_reliability: Source credibility score (0-1)
            db: Database session (optional, for deduplication check)
        
        Returns:
            Event object or None if processing fails
        """
        try:
            logger.info(f"Processing article: {title[:50]}...")
            
            # Deduplication check
            content_hash = self._hash_content(content)
            if db and self._is_duplicate(content_hash, db):
                logger.info(f"Skipping duplicate content: {title[:50]}")
                return None
            
            # Step 1: Extract entities
            entities = self.nlp.extract_entities(content)
            logger.debug(f"Extracted entities: {entities}")
            
            # Step 2: Identify and geocode primary location
            locations = entities.get("locations", [])
            if not locations:
                logger.warning(f"No locations found in article: {title}")
                return None
            
            primary_location_name = self.geocoder.identify_primary_location(locations)
            primary_coords = self.geocoder.geocode_location(primary_location_name)
            
            if not primary_coords:
                logger.warning(f"Could not geocode primary location: {primary_location_name}")
                return None
            
            # Step 3: Geocode secondary locations
            secondary_location_names = [loc for loc in locations if loc != primary_location_name][:5]
            secondary_locations = self.geocoder.geocode_multiple(secondary_location_names)
            
            # Step 4: Generate summary
            summary = self.nlp.summarize_text(content)
            
            # Step 5: Classify event type
            event_type, classification_confidence = self.nlp.classify_event_type(content)
            
            # Step 6: Extract topics
            topics = self.nlp.extract_topics(content)
            
            # Step 7: Generate analyst-style analysis
            analysis = self._generate_analysis(
                event_type=event_type,
                entities=entities,
                primary_location=primary_location_name,
                topics=topics
            )
            
            # Step 8: Calculate overall confidence
            ner_confidence = self._estimate_ner_confidence(entities)
            confidence = self.nlp.calculate_confidence(
                ner_confidence=ner_confidence,
                classification_confidence=classification_confidence,
                source_reliability=source_reliability
            )
            
            # Step 9: Construct Event object
            event = Event(
                event_title=title,
                summary=summary,
                analysis=analysis,
                primary_location_name=primary_location_name,
                primary_location=from_shape(Point(primary_coords[1], primary_coords[0]), srid=4326),
                secondary_locations=secondary_locations,
                entities=entities,
                topics=topics,
                event_type=event_type,
                source_urls=[source_url],
                source_type=source_type,
                published_date=published_date,
                confidence=confidence,
                quality_score=source_reliability,
                raw_content_hash=content_hash,
                processing_version="1.0"
            )
            
            logger.info(f"Successfully processed event: {title[:50]} (confidence: {confidence:.2f})")
            return event
            
        except Exception as e:
            logger.error(f"Failed to process article '{title}': {e}", exc_info=True)
            return None
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _is_duplicate(self, content_hash: str, db: Session) -> bool:
        """Check if content already exists in database."""
        existing = db.query(Event).filter(Event.raw_content_hash == content_hash).first()
        return existing is not None
    
    def _estimate_ner_confidence(self, entities: Dict) -> float:
        """
        Estimate NER confidence based on entity richness.
        More entities (especially locations) indicates higher confidence.
        """
        total_entities = sum(len(v) for v in entities.values())
        location_count = len(entities.get("locations", []))
        org_count = len(entities.get("organizations", []))
        
        # Heuristic scoring
        if total_entities == 0:
            return 0.1
        elif location_count == 0:
            return 0.3
        elif location_count >= 2 and org_count >= 1:
            return 0.8
        elif location_count >= 1:
            return 0.6
        else:
            return 0.4
    
    def _generate_analysis(
        self,
        event_type: str,
        entities: Dict,
        primary_location: str,
        topics: list
    ) -> str:
        """
        Generate analyst-style significance explanation.
        Provides context about why this event matters.
        """
        organizations = entities.get("organizations", [])
        org_text = f"involving {', '.join(organizations[:3])}" if organizations else ""
        
        topic_text = f"related to {', '.join(topics[:3])}" if topics else ""
        
        analysis = (
            f"This {event_type} in {primary_location} {org_text} is significant for "
            f"regional security monitoring. "
        )
        
        if topic_text:
            analysis += f"The event is {topic_text}. "
        
        analysis += (
            "This assessment is based on publicly available reporting and should be "
            "corroborated with additional sources."
        )
        
        return analysis


# Singleton instance
event_processor = EventProcessor()
