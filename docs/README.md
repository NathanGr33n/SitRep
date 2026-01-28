# SitRep - Security Event Intelligence Dashboard

**A full-stack dashboard for ingesting, processing, and visualizing global security events from public sources.**

---

## **Overview**

SitRep collects publicly available information from news outlets, government sources, think tanks, and social media to extract structured security-related events. These events are processed using NLP (Hugging Face Transformers), geocoded, and displayed on an interactive global map powered by Mapbox GL JS.

### **Key Features**

- **Automated Ingestion**: RSS feeds, APIs, and web scraping from public sources
- **NLP Processing**: Entity extraction, summarization, and classification using Hugging Face models
- **Geospatial Analysis**: PostGIS-powered location queries and event clustering
- **Interactive Map**: Mapbox GL JS with marker clustering and filtering
- **Confidence Scoring**: Transparent uncertainty assessment for each event
- **Analyst Context**: AI-generated significance explanations

---

## **Architecture**

```
┌─────────────────┐
│   Data Sources  │ (RSS, APIs, Social Media)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ingestion      │ (RSS Parser, HTTP Clients)
│  Pipeline       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  NLP Engine     │ (Hugging Face Transformers)
│                 │ - Entity Extraction (NER)
│                 │ - Summarization (BART)
│                 │ - Classification (Zero-Shot)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Geocoding      │ (Nominatim/OSM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │ (PostGIS for geospatial data)
│  Database       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │ (REST API)
│  Backend        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Mapbox GL JS   │ (Interactive Map UI)
│  Frontend       │
└─────────────────┘
```

---

## **Tech Stack**

### **Backend**
- **Python 3.11+**
- **FastAPI**: High-performance async API framework
- **SQLAlchemy + PostGIS**: Geospatial database ORM
- **Hugging Face Transformers**: NLP models
- **Celery + Redis**: Background task queue
- **Geopy**: Geocoding via Nominatim

### **Frontend**
- **HTML/CSS/JavaScript**: Vanilla JS (no framework dependencies)
- **Mapbox GL JS**: Interactive map visualization
- **Responsive Design**: Mobile-friendly UI

### **Infrastructure**
- **PostgreSQL 15 + PostGIS 3.3**: Geospatial database
- **Docker + Docker Compose**: Containerized deployment
- **Nginx**: Static file serving and reverse proxy

---

## **Quick Start**

### **Prerequisites**
- Docker & Docker Compose
- Mapbox API Token ([Get one free](https://account.mapbox.com/))

### **1. Clone Repository**
```bash
git clone https://github.com/NathanGr33n/SitRep.git
cd SitRep
```

### **2. Configure Environment**
```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env and set your configurations
```

### **3. Set Mapbox Token**
Edit `frontend/src/components/map.js` and replace:
```javascript
const MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE';
```

### **4. Start Services**
```bash
docker-compose up -d
```

### **5. Initialize Database**
```bash
docker exec -it sitrep_backend python -c "from app.database import init_db; init_db()"
```

### **6. Access Dashboard**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## **Development Setup**

### **Backend Development**

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Development Server**
```bash
uvicorn app.main:app --reload
```

### **Frontend Development**

Frontend uses vanilla JavaScript - simply edit files in `frontend/src/` and refresh your browser.

For local development without Docker:
```bash
cd frontend/public
python -m http.server 3000
```

---

## **Usage**

### **Adding Data Sources**

To add RSS feeds to the system, use the example feeds in `backend/app/pipelines/rss_ingester.py`:

```python
from app.pipelines.rss_ingester import rss_ingester
from app.pipelines.event_processor import event_processor
from app.database import SessionLocal

# Fetch and process a feed
db = SessionLocal()
articles = rss_ingester.fetch_feed("https://example.com/rss")

for article in articles:
    event = event_processor.process_article(
        title=article['title'],
        content=article['content'],
        source_url=article['url'],
        published_date=article['published_date'],
        source_type='news',
        source_reliability=0.7,
        db=db
    )
    if event:
        db.add(event)

db.commit()
```

### **API Endpoints**

#### **Get Events**
```http
GET /api/events?limit=1000&event_type=military%20exercise
```

#### **Get GeoJSON for Map**
```http
GET /api/events/geojson?days_back=30&min_confidence=0.5
```

#### **Get Event Details**
```http
GET /api/events/{event_id}
```

#### **Search Nearby Events**
```http
GET /api/events/search/nearby?lat=40.7128&lon=-74.0060&radius_km=100
```

#### **Get Statistics**
```http
GET /api/events/stats/summary?days_back=30
```

---

## **Configuration**

### **Environment Variables**

See `backend/.env.example` for all configuration options:

- **Database**: `DATABASE_URL`
- **NLP Models**: `NER_MODEL`, `SUMMARIZATION_MODEL`, `CLASSIFICATION_MODEL`
- **Geocoding**: `GEOCODING_USER_AGENT`, `GEOCODING_RATE_LIMIT`
- **Confidence Thresholds**: `MIN_CONFIDENCE_SCORE`, `HIGH_CONFIDENCE_THRESHOLD`
- **Clustering**: `CLUSTER_DISTANCE_KM`, `CLUSTER_TIME_WINDOW_HOURS`

---

## **Data Model**

### **Event Schema**
```json
{
  "id": 123,
  "event_title": "Military Exercise in Baltic Sea",
  "summary": "NATO conducts joint naval exercises...",
  "analysis": "This military exercise is significant for...",
  "primary_location": {
    "name": "Baltic Sea",
    "lat": 58.0,
    "lon": 20.0
  },
  "secondary_locations": [...],
  "entities": {
    "organizations": ["NATO", "US Navy"],
    "locations": ["Poland", "Lithuania"],
    "persons": []
  },
  "topics": ["military", "geopolitical"],
  "event_type": "military exercise",
  "source_urls": ["https://..."],
  "published_date": "2026-01-27T10:00:00",
  "confidence": 0.85
}
```

---

## **Deployment**

### **Production Deployment**

1. **Set Production Environment Variables**
```bash
# Use strong passwords and secure secrets
export DATABASE_URL="postgresql://user:password@host:5432/db"
export MAPBOX_ACCESS_TOKEN="your_production_token"
```

2. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Configure HTTPS** (use Nginx + Let's Encrypt)

4. **Set up Celery Workers** for background ingestion

---

## **Safety & Compliance**

- **Public Data Only**: All sources must be publicly available
- **No Sensitive Intelligence**: System does not handle classified or OSINT
- **Transparent Uncertainty**: All events include confidence scores
- **Attribution**: Sources are always linked
- **Privacy**: No personal data collection

---

## **Troubleshooting**

### **Backend Won't Start**
- Check PostgreSQL is running: `docker ps`
- Verify database connection: `docker logs sitrep_backend`
- Ensure PostGIS extension is enabled

### **Map Not Loading**
- Verify Mapbox token is set in `frontend/src/components/map.js`
- Check browser console for errors
- Ensure backend API is accessible

### **NLP Models Download Slowly**
- Models are downloaded on first use (~500MB-2GB total)
- Use a GPU for faster inference (set `CUDA_VISIBLE_DEVICES`)

---

## **Contributing**

Contributions welcome! Please follow:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## **License**

MIT License - See LICENSE file for details

---

## **Contact**

For questions or issues, please open a GitHub issue or contact the maintainers.
