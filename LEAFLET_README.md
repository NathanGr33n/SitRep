# SitRep - Leaflet.js Branch

**This branch uses Leaflet.js with OpenStreetMap tiles instead of Mapbox GL JS.**

## Why Leaflet.js?

- ✅ **100% Free & Open Source** - No API tokens or usage limits
- ✅ **OpenStreetMap Tiles** - Free, community-maintained map data
- ✅ **No Vendor Lock-in** - Complete control over your mapping infrastructure
- ✅ **Lighter Weight** - Smaller bundle size than Mapbox GL JS
- ✅ **Battle-Tested** - Industry standard for 10+ years

## Key Differences from Main Branch

| Feature | Main (Mapbox) | Leaflet Branch |
|---------|---------------|----------------|
| **Cost** | Free tier: 50k loads/month | Completely free, unlimited |
| **Map Style** | Mapbox Dark v11 | CartoDB Dark Matter (OSM) |
| **3D/Globe** | ✅ Yes | ❌ 2D only |
| **Performance** | WebGL-accelerated | Canvas-based (slightly slower at scale) |
| **API Token** | Required | Not required |
| **Clustering** | Built-in | Via leaflet.markercluster plugin |

## Quick Start

No changes needed to the backend! The only difference is in the frontend.

### 1. Clone and Switch to Leaflet Branch

```bash
git clone https://github.com/NathanGr33n/SitRep.git
cd SitRep
git checkout leaflet-alternative
```

### 2. No Configuration Required!

Unlike the Mapbox version, you don't need any API tokens or configuration.

### 3. Start Services

```bash
docker-compose up -d
```

### 4. Access Dashboard

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000

That's it! No Mapbox token needed.

## Map Tile Providers

This branch uses **CartoDB Dark Matter** tiles by default, which are:
- Free to use
- No registration required
- Dark theme to match the dashboard

### Alternative Free Tile Providers

You can easily switch to other providers by editing `frontend/src/components/map.js`:

#### OpenStreetMap Standard
```javascript
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(this.map);
```

#### Stamen Toner (B&W)
```javascript
L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.png', {
    attribution: 'Map tiles by Stamen Design, CC BY 3.0'
}).addTo(this.map);
```

#### ESRI World Imagery (Satellite)
```javascript
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri'
}).addTo(this.map);
```

## Features Supported

✅ Event markers with confidence-based colors
✅ Marker clustering (via leaflet.markercluster)
✅ Popups with event details
✅ Click to view full event information
✅ Filtering by date, type, confidence
✅ Geospatial queries (nearby events)
✅ Dark theme integration

## Limitations vs Mapbox

- **No 3D globe projection** - Map is 2D Mercator only
- **No vector tiles** - Uses raster tiles (slightly slower at scale)
- **Basic styling** - Can't customize map style as extensively
- **Performance** - Handles thousands of markers, but not as smooth as Mapbox GL JS with hundreds of thousands

## When to Use This Branch

Use **Leaflet branch** if:
- You want zero dependencies on third-party services
- You need completely free, unlimited map loads
- You're building an internal/private tool
- You prioritize simplicity over advanced features
- Budget is a constraint

Use **Mapbox main branch** if:
- You need 3D globe visualization
- Performance with 100k+ markers is critical
- You want advanced map styling
- Free tier limits (50k/month) are sufficient

## Self-Hosting Tiles (Advanced)

For complete independence, you can self-host your own tile server:

1. **Use OpenMapTiles** - https://openmaptiles.org/
2. **Set up tile server** - https://github.com/maptiler/tileserver-gl
3. **Update tile URL** in map.js to point to your server

This gives you 100% control but requires significant infrastructure.

## Contributing

This branch stays in sync with main branch features, with only the map library differing. Pull requests welcome!

## License

MIT License - Same as main branch

---

**No API tokens. No limits. Just maps.**
