/**
 * Map Component
 * Handles Leaflet.js map initialization and event visualization
 * Uses OpenStreetMap tiles (100% free and open source)
 */

class MapComponent {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.markerCluster = null;
        this.markers = [];
        this.onEventClick = null;
    }

    /**
     * Initialize the map
     */
    init(onEventClickCallback) {
        this.onEventClick = onEventClickCallback;

        // Create Leaflet map
        this.map = L.map(this.containerId, {
            center: [20, 0], // Global view
            zoom: 2,
            minZoom: 2,
            maxZoom: 18,
            worldCopyJump: true
        });

        // Add dark-themed OpenStreetMap tiles (CartoDB Dark Matter)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(this.map);

        // Add scale control
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(this.map);

        // Initialize marker cluster group
        this.markerCluster = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true,
            iconCreateFunction: (cluster) => {
                const count = cluster.getChildCount();
                let size = 'small';
                if (count > 30) size = 'large';
                else if (count > 10) size = 'medium';
                
                return L.divIcon({
                    html: `<div><span>${count}</span></div>`,
                    className: `marker-cluster marker-cluster-${size}`,
                    iconSize: L.point(40, 40)
                });
            }
        });

        this.map.addLayer(this.markerCluster);

        console.log('Map loaded successfully');
    }

    /**
     * Load events onto the map as clustered points
     */
    loadEvents(geojsonData) {
        // Clear existing markers
        this.clearEvents();

        // Create markers for each event
        geojsonData.features.forEach(feature => {
            const coords = feature.geometry.coordinates;
            const props = feature.properties;

            // Determine marker color based on confidence
            let markerColor = '#f44336'; // Low confidence (red)
            if (props.confidence >= 0.7) markerColor = '#4caf50'; // High (green)
            else if (props.confidence >= 0.5) markerColor = '#ffc107'; // Medium (yellow)

            // Create custom icon
            const icon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="
                    background-color: ${markerColor};
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    border: 3px solid white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                "></div>`,
                iconSize: [22, 22],
                iconAnchor: [11, 11]
            });

            // Create marker
            const marker = L.marker([coords[1], coords[0]], { icon });

            // Create popup content
            const popupContent = `
                <div class="leaflet-popup-custom">
                    <div class="popup-title">${props.title}</div>
                    <div class="popup-type">${props.event_type}</div>
                    <p style="margin-top: 0.5rem; font-size: 0.85rem;">
                        ${props.summary ? props.summary.substring(0, 100) + '...' : 'No summary available'}
                    </p>
                    <button onclick="mapComponent.onEventClick(${props.id})" 
                            style="margin-top: 0.5rem; padding: 0.5rem 1rem; background-color: #64b5f6; 
                                   border: none; border-radius: 4px; color: #0a0e27; 
                                   font-weight: bold; cursor: pointer; width: 100%;">
                        View Details
                    </button>
                </div>
            `;

            marker.bindPopup(popupContent, {
                maxWidth: 300,
                className: 'custom-popup'
            });

            // Add marker to cluster group
            this.markerCluster.addLayer(marker);
            this.markers.push(marker);
        });

        console.log(`Loaded ${geojsonData.features.length} events to map`);
    }

    /**
     * Clear all events from the map
     */
    clearEvents() {
        if (this.markerCluster) {
            this.markerCluster.clearLayers();
            this.markers = [];
        }
    }

    /**
     * Fly to a specific location
     */
    flyTo(lat, lon, zoom = 10) {
        this.map.flyTo([lat, lon], zoom, {
            duration: 2
        });
    }
}

// Export singleton instance
const mapComponent = new MapComponent('map');
