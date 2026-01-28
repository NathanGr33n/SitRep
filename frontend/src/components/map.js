/**
 * Map Component
 * Handles Mapbox GL JS map initialization and event visualization
 */

const MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE'; // Replace with actual token

class MapComponent {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.onEventClick = null;
    }

    /**
     * Initialize the map
     */
    init(onEventClickCallback) {
        this.onEventClick = onEventClickCallback;

        mapboxgl.accessToken = MAPBOX_TOKEN;
        
        this.map = new mapboxgl.Map({
            container: this.containerId,
            style: 'mapbox://styles/mapbox/dark-v11',
            center: [0, 20], // Global view
            zoom: 2,
            projection: 'globe'
        });

        // Add navigation controls
        this.map.addControl(new mapboxgl.NavigationControl());

        // Add scale control
        this.map.addControl(new mapboxgl.ScaleControl({
            maxWidth: 200,
            unit: 'metric'
        }));

        this.map.on('load', () => {
            console.log('Map loaded successfully');
            
            // Add atmosphere effect
            this.map.setFog({
                color: 'rgb(186, 210, 235)',
                'high-color': 'rgb(36, 92, 223)',
                'horizon-blend': 0.02,
                'space-color': 'rgb(11, 11, 25)',
                'star-intensity': 0.6
            });
        });
    }

    /**
     * Load events onto the map as clustered points
     */
    loadEvents(geojsonData) {
        if (!this.map.getSource('events')) {
            // Add source
            this.map.addSource('events', {
                type: 'geojson',
                data: geojsonData,
                cluster: true,
                clusterMaxZoom: 14,
                clusterRadius: 50
            });

            // Add cluster circle layer
            this.map.addLayer({
                id: 'clusters',
                type: 'circle',
                source: 'events',
                filter: ['has', 'point_count'],
                paint: {
                    'circle-color': [
                        'step',
                        ['get', 'point_count'],
                        '#64b5f6',
                        10,
                        '#42a5f5',
                        30,
                        '#2196f3'
                    ],
                    'circle-radius': [
                        'step',
                        ['get', 'point_count'],
                        20,
                        10,
                        30,
                        30,
                        40
                    ],
                    'circle-opacity': 0.8
                }
            });

            // Add cluster count label
            this.map.addLayer({
                id: 'cluster-count',
                type: 'symbol',
                source: 'events',
                filter: ['has', 'point_count'],
                layout: {
                    'text-field': '{point_count_abbreviated}',
                    'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                    'text-size': 12
                },
                paint: {
                    'text-color': '#ffffff'
                }
            });

            // Add unclustered points
            this.map.addLayer({
                id: 'unclustered-point',
                type: 'circle',
                source: 'events',
                filter: ['!', ['has', 'point_count']],
                paint: {
                    'circle-color': [
                        'case',
                        ['>=', ['get', 'confidence'], 0.7], '#4caf50', // High confidence
                        ['>=', ['get', 'confidence'], 0.5], '#ffc107', // Medium confidence
                        '#f44336' // Low confidence
                    ],
                    'circle-radius': 8,
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#fff',
                    'circle-opacity': 0.9
                }
            });

            // Click event for clusters
            this.map.on('click', 'clusters', (e) => {
                const features = this.map.queryRenderedFeatures(e.point, {
                    layers: ['clusters']
                });
                const clusterId = features[0].properties.cluster_id;
                this.map.getSource('events').getClusterExpansionZoom(
                    clusterId,
                    (err, zoom) => {
                        if (err) return;
                        this.map.easeTo({
                            center: features[0].geometry.coordinates,
                            zoom: zoom
                        });
                    }
                );
            });

            // Click event for unclustered points
            this.map.on('click', 'unclustered-point', (e) => {
                const coordinates = e.features[0].geometry.coordinates.slice();
                const properties = e.features[0].properties;

                // Ensure proper coordinate wrapping for antimeridian
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }

                // Show popup
                new mapboxgl.Popup()
                    .setLngLat(coordinates)
                    .setHTML(`
                        <div class="popup-title">${properties.title}</div>
                        <div class="popup-type">${properties.event_type}</div>
                        <p style="margin-top: 0.5rem; font-size: 0.85rem;">
                            ${properties.summary.substring(0, 100)}...
                        </p>
                        <button onclick="mapComponent.onEventClick(${properties.id})" 
                                style="margin-top: 0.5rem; padding: 0.5rem 1rem; background-color: #64b5f6; 
                                       border: none; border-radius: 4px; color: #0a0e27; 
                                       font-weight: bold; cursor: pointer;">
                            View Details
                        </button>
                    `)
                    .addTo(this.map);
            });

            // Change cursor on hover
            this.map.on('mouseenter', 'clusters', () => {
                this.map.getCanvas().style.cursor = 'pointer';
            });
            this.map.on('mouseleave', 'clusters', () => {
                this.map.getCanvas().style.cursor = '';
            });
            this.map.on('mouseenter', 'unclustered-point', () => {
                this.map.getCanvas().style.cursor = 'pointer';
            });
            this.map.on('mouseleave', 'unclustered-point', () => {
                this.map.getCanvas().style.cursor = '';
            });

        } else {
            // Update existing source
            this.map.getSource('events').setData(geojsonData);
        }
    }

    /**
     * Clear all events from the map
     */
    clearEvents() {
        if (this.map.getSource('events')) {
            this.map.getSource('events').setData({
                type: 'FeatureCollection',
                features: []
            });
        }
    }

    /**
     * Fly to a specific location
     */
    flyTo(lat, lon, zoom = 10) {
        this.map.flyTo({
            center: [lon, lat],
            zoom: zoom,
            duration: 2000
        });
    }
}

// Export singleton instance
const mapComponent = new MapComponent('map');
