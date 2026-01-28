# SitRep - Security Event Intelligence Dashboard

**A full-stack dashboard for ingesting, processing, and visualizing global security events from public sources.**

![SitRep Dashboard](docs/architecture.png)

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/NathanGr33n/SitRep.git
cd SitRep

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# 3. Set Mapbox token in frontend/src/components/map.js

# 4. Start services
docker-compose up -d

# 5. Initialize database
docker exec -it sitrep_backend python -c "from app.database import init_db; init_db()"

# 6. Access dashboard at http://localhost:3000
```

## Features

- ✅ **NLP-Powered Event Extraction** - Hugging Face Transformers for entity extraction, summarization, and classification
- ✅ **Geospatial Intelligence** - PostGIS database with location-based queries
- ✅ **Interactive Map** - Mapbox GL JS with clustering and real-time filtering
- ✅ **Multi-Source Ingestion** - RSS feeds, APIs, social media, and government sources
- ✅ **Confidence Scoring** - Transparent uncertainty assessment for every event
- ✅ **Production Ready** - Docker Compose deployment with PostgreSQL, Redis, and FastAPI

## Tech Stack

**Backend**: Python • FastAPI • SQLAlchemy • PostGIS • Hugging Face Transformers • Celery  
**Frontend**: JavaScript • Mapbox GL JS • HTML/CSS  
**Infrastructure**: Docker • PostgreSQL • Redis • Nginx

## Documentation

Full documentation available in [`docs/README.md`](docs/README.md)

- [Architecture Overview](docs/README.md#architecture)
- [API Documentation](http://localhost:8000/docs) (after starting services)
- [Development Guide](docs/README.md#development-setup)
- [Deployment Instructions](docs/README.md#deployment)

## Project Structure

```
sitrep/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # REST API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # NLP & geocoding services
│   │   ├── pipelines/    # Data ingestion pipelines
│   │   └── main.py       # Application entry point
│   └── requirements.txt
├── frontend/             # Mapbox GL JS frontend
│   ├── public/          # Static HTML
│   └── src/             # JavaScript components
├── database/            # Database migrations
├── docs/                # Documentation
├── docker-compose.yml   # Docker services
└── README.md
```

## Safety & Compliance

- **Public Data Only**: All sources must be publicly available
- **Transparent Uncertainty**: All events include confidence scores
- **Attribution**: Sources are always linked
- **No Sensitive Intelligence**: System does not handle classified data

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

---

**Built with ❤️ for security professionals and analysts**

# SitRep
OSINT for breaking news analysis and confirmation
