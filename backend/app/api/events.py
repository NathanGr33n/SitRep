"""
API endpoints for events.
Provides RESTful API for querying and filtering events.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_DWithin, ST_GeogFromText

from app.database import get_db
from app.models.event import Event
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/")
def get_events(
    db: Session = Depends(get_db),
    limit: int = Query(default=1000, le=5000),
    offset: int = Query(default=0, ge=0),
    event_type: Optional[str] = None,
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    country: Optional[str] = None,
    topic: Optional[str] = None
):
    """
    Get events with optional filters.
    
    Query parameters:
    - limit: Maximum number of events to return
    - offset: Number of events to skip (for pagination)
    - event_type: Filter by event type
    - min_confidence: Minimum confidence score
    - start_date: Filter events after this date
    - end_date: Filter events before this date
    - country: Filter by country name
    - topic: Filter by topic tag
    
    Returns:
    - List of events as dictionaries
    """
    try:
        query = db.query(Event)
        
        # Apply filters
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        if min_confidence is not None:
            query = query.filter(Event.confidence >= min_confidence)
        else:
            # Default: filter by configured minimum
            query = query.filter(Event.confidence >= settings.min_confidence_score)
        
        if start_date:
            query = query.filter(Event.published_date >= start_date)
        
        if end_date:
            query = query.filter(Event.published_date <= end_date)
        
        if country:
            # Filter by primary location name containing country
            query = query.filter(Event.primary_location_name.ilike(f"%{country}%"))
        
        if topic:
            # Filter by topic in JSON array
            query = query.filter(Event.topics.contains([topic]))
        
        # Order by date (most recent first)
        query = query.order_by(Event.published_date.desc())
        
        # Apply pagination
        events = query.offset(offset).limit(limit).all()
        
        return {
            "count": len(events),
            "events": [event.to_dict() for event in events]
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/geojson")
def get_events_geojson(
    db: Session = Depends(get_db),
    limit: int = Query(default=1000, le=5000),
    event_type: Optional[str] = None,
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    days_back: int = Query(default=30, ge=1, le=365)
):
    """
    Get events as GeoJSON FeatureCollection for map display.
    
    Query parameters:
    - limit: Maximum number of events
    - event_type: Filter by event type
    - min_confidence: Minimum confidence score
    - days_back: Number of days to look back from today
    
    Returns:
    - GeoJSON FeatureCollection
    """
    try:
        query = db.query(Event)
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(Event.published_date >= cutoff_date)
        
        # Apply filters
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        if min_confidence is not None:
            query = query.filter(Event.confidence >= min_confidence)
        else:
            query = query.filter(Event.confidence >= settings.min_confidence_score)
        
        # Order and limit
        query = query.order_by(Event.published_date.desc()).limit(limit)
        
        events = query.all()
        
        features = [event.to_geojson_feature() for event in events]
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch GeoJSON: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get a single event by ID.
    
    Args:
    - event_id: Event ID
    
    Returns:
    - Event details as dictionary
    """
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return event.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary")
def get_stats(
    db: Session = Depends(get_db),
    days_back: int = Query(default=30, ge=1, le=365)
):
    """
    Get statistics summary for dashboard.
    
    Query parameters:
    - days_back: Number of days to analyze
    
    Returns:
    - Statistics including event counts, types, and trends
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Total events
        total_events = db.query(func.count(Event.id)).filter(
            Event.published_date >= cutoff_date
        ).scalar()
        
        # Events by type
        events_by_type = db.query(
            Event.event_type,
            func.count(Event.id).label("count")
        ).filter(
            Event.published_date >= cutoff_date
        ).group_by(Event.event_type).all()
        
        # High confidence events
        high_confidence_count = db.query(func.count(Event.id)).filter(
            and_(
                Event.published_date >= cutoff_date,
                Event.confidence >= settings.high_confidence_threshold
            )
        ).scalar()
        
        return {
            "total_events": total_events,
            "high_confidence_count": high_confidence_count,
            "events_by_type": {
                event_type: count for event_type, count in events_by_type
            },
            "date_range": {
                "start": cutoff_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/nearby")
def search_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, le=500)
):
    """
    Search for events near a specific location.
    
    Query parameters:
    - lat: Latitude
    - lon: Longitude
    - radius_km: Search radius in kilometers
    - limit: Maximum number of results
    
    Returns:
    - List of nearby events
    """
    try:
        # Create point geometry for search center
        point_wkt = f"POINT({lon} {lat})"
        
        # Query events within radius using PostGIS
        events = db.query(Event).filter(
            ST_DWithin(
                Event.primary_location,
                ST_GeogFromText(point_wkt),
                radius_km * 1000  # Convert km to meters
            )
        ).order_by(Event.published_date.desc()).limit(limit).all()
        
        return {
            "count": len(events),
            "search_center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "events": [event.to_dict() for event in events]
        }
        
    except Exception as e:
        logger.error(f"Failed to search nearby events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
