"""
SQLAlchemy models for security events.
Uses PostGIS for geospatial data.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, Index
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

from app.database import Base


class Event(Base):
    """
    Security event model with geospatial data.
    Represents a processed and geocoded security event.
    """
    __tablename__ = "events"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Event metadata
    event_title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    analysis = Column(Text)  # Analyst-style significance explanation
    
    # Locations (PostGIS geometry)
    primary_location_name = Column(String(255), nullable=False, index=True)
    primary_location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    # Secondary locations stored as JSON with coordinates
    secondary_locations = Column(JSON, default=list)  # [{"name": "...", "lat": ..., "lon": ...}, ...]
    
    # Entities (structured JSON)
    entities = Column(JSON, default=dict)  # {"organizations": [], "locations": [], "other": []}
    
    # Classification and tags
    topics = Column(JSON, default=list)  # ["military", "cyber", "infrastructure", ...]
    event_type = Column(String(100), index=True)  # Classified event category
    
    # Source information
    source_urls = Column(JSON, default=list)
    source_type = Column(String(50))  # "news", "government", "social", "report"
    
    # Temporal data
    published_date = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Confidence and quality
    confidence = Column(Float, nullable=False, index=True)  # 0.0 to 1.0
    quality_score = Column(Float)  # Source reliability + NLP confidence
    
    # Clustering
    cluster_id = Column(String(100), index=True)  # Groups related events
    is_cluster_primary = Column(Boolean, default=False)  # Main event in cluster
    
    # Processing metadata
    processing_version = Column(String(20))  # Track NLP model version
    raw_content_hash = Column(String(64), index=True)  # Deduplication
    
    # Indexes for geospatial queries
    __table_args__ = (
        Index('idx_event_location', 'primary_location', postgresql_using='gist'),
        Index('idx_event_date_confidence', 'published_date', 'confidence'),
        Index('idx_event_type_date', 'event_type', 'published_date'),
    )
    
    def to_dict(self):
        """Convert event to dictionary for API response."""
        # Convert PostGIS geometry to lat/lon
        point = to_shape(self.primary_location)
        
        return {
            "id": self.id,
            "event_title": self.event_title,
            "summary": self.summary,
            "analysis": self.analysis,
            "primary_location": {
                "name": self.primary_location_name,
                "lat": point.y,
                "lon": point.x
            },
            "secondary_locations": self.secondary_locations or [],
            "entities": self.entities or {},
            "topics": self.topics or [],
            "event_type": self.event_type,
            "source_urls": self.source_urls or [],
            "source_type": self.source_type,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "confidence": self.confidence,
            "cluster_id": self.cluster_id,
            "is_cluster_primary": self.is_cluster_primary
        }
    
    def to_geojson_feature(self):
        """Convert event to GeoJSON feature for map display."""
        point = to_shape(self.primary_location)
        
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point.x, point.y]
            },
            "properties": {
                "id": self.id,
                "title": self.event_title,
                "summary": self.summary,
                "event_type": self.event_type,
                "confidence": self.confidence,
                "published_date": self.published_date.isoformat() if self.published_date else None,
                "cluster_id": self.cluster_id
            }
        }


class Source(Base):
    """
    Data source configuration.
    Tracks RSS feeds, APIs, and other ingestion endpoints.
    """
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # "rss", "api", "scraper"
    url = Column(String(1000), nullable=False)
    enabled = Column(Boolean, default=True)
    reliability_score = Column(Float, default=0.5)  # Source credibility
    last_ingested_at = Column(DateTime)
    ingestion_frequency_hours = Column(Integer, default=6)
    metadata = Column(JSON, default=dict)  # Source-specific configuration
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
