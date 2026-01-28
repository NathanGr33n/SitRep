"""
NLP service using Hugging Face Transformers.
Handles entity extraction, summarization, and event classification.
"""
import logging
from typing import Dict, List, Tuple
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    AutoModelForSeq2SeqLM,
    pipeline
)

from app.config import settings

logger = logging.getLogger(__name__)


class NLPService:
    """
    Service for NLP operations using Hugging Face models.
    Lazily loads models on first use to reduce startup time.
    """
    
    def __init__(self):
        self._ner_pipeline = None
        self._summarizer = None
        self._classifier = None
        self.device = 0 if torch.cuda.is_available() else -1
        
    @property
    def ner_pipeline(self):
        """Lazy load NER pipeline."""
        if self._ner_pipeline is None:
            logger.info(f"Loading NER model: {settings.ner_model}")
            self._ner_pipeline = pipeline(
                "ner",
                model=settings.ner_model,
                aggregation_strategy="simple",
                device=self.device
            )
        return self._ner_pipeline
    
    @property
    def summarizer(self):
        """Lazy load summarization pipeline."""
        if self._summarizer is None:
            logger.info(f"Loading summarization model: {settings.summarization_model}")
            self._summarizer = pipeline(
                "summarization",
                model=settings.summarization_model,
                device=self.device
            )
        return self._summarizer
    
    @property
    def classifier(self):
        """Lazy load zero-shot classification pipeline."""
        if self._classifier is None:
            logger.info(f"Loading classification model: {settings.classification_model}")
            self._classifier = pipeline(
                "zero-shot-classification",
                model=settings.classification_model,
                device=self.device
            )
        return self._classifier
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        Returns categorized entities: organizations, locations, persons, etc.
        """
        try:
            entities_raw = self.ner_pipeline(text)
            
            # Categorize entities
            entities = {
                "organizations": [],
                "locations": [],
                "persons": [],
                "other": []
            }
            
            for entity in entities_raw:
                entity_text = entity["word"]
                entity_type = entity["entity_group"]
                
                # Map entity types to categories
                if entity_type in ["ORG", "ORGANIZATION"]:
                    entities["organizations"].append(entity_text)
                elif entity_type in ["LOC", "GPE", "LOCATION"]:
                    entities["locations"].append(entity_text)
                elif entity_type in ["PER", "PERSON"]:
                    entities["persons"].append(entity_text)
                else:
                    entities["other"].append(entity_text)
            
            # Deduplicate
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"organizations": [], "locations": [], "persons": [], "other": []}
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate a concise summary of the text.
        Handles long texts by truncating to model's max input length.
        """
        try:
            # Truncate if text is too long (BART max is ~1024 tokens)
            max_input_length = 1024
            tokenizer = self.summarizer.tokenizer
            tokens = tokenizer.encode(text, truncation=True, max_length=max_input_length)
            text_truncated = tokenizer.decode(tokens, skip_special_tokens=True)
            
            summary = self.summarizer(
                text_truncated,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]["summary_text"]
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Fallback: return first N characters
            return text[:300] + "..." if len(text) > 300 else text
    
    def classify_event_type(self, text: str) -> Tuple[str, float]:
        """
        Classify event type using zero-shot classification.
        Returns (event_type, confidence_score).
        """
        candidate_labels = [
            "military exercise",
            "cyber attack",
            "infrastructure incident",
            "diplomatic event",
            "security threat",
            "terrorist activity",
            "natural disaster impact",
            "political instability",
            "border incident",
            "weapons development",
            "energy security",
            "other security event"
        ]
        
        try:
            result = self.classifier(text, candidate_labels)
            event_type = result["labels"][0]
            confidence = result["scores"][0]
            
            return event_type, confidence
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "unknown", 0.0
    
    def extract_topics(self, text: str, top_k: int = 5) -> List[str]:
        """
        Extract relevant security-related topics from text.
        Uses zero-shot classification with topic candidates.
        """
        topic_candidates = [
            "military",
            "cyber security",
            "terrorism",
            "infrastructure",
            "energy",
            "maritime",
            "aviation",
            "space",
            "nuclear",
            "intelligence",
            "border security",
            "counterterrorism",
            "weapons",
            "defense technology",
            "geopolitical"
        ]
        
        try:
            result = self.classifier(text, topic_candidates, multi_label=True)
            
            # Return top K topics with confidence > 0.3
            topics = [
                label for label, score in zip(result["labels"], result["scores"])
                if score > 0.3
            ][:top_k]
            
            return topics
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
    
    def calculate_confidence(
        self,
        ner_confidence: float,
        classification_confidence: float,
        source_reliability: float
    ) -> float:
        """
        Calculate overall confidence score for an event.
        Combines NER quality, classification confidence, and source reliability.
        """
        # Weighted average
        weights = {
            "ner": 0.3,
            "classification": 0.4,
            "source": 0.3
        }
        
        confidence = (
            weights["ner"] * ner_confidence +
            weights["classification"] * classification_confidence +
            weights["source"] * source_reliability
        )
        
        return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]


# Singleton instance
nlp_service = NLPService()
