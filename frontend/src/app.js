/**
 * Main Application
 * Orchestrates all components and manages application state
 */

class SitRepApp {
    constructor() {
        this.loadingIndicator = document.getElementById('loading-indicator');
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing SitRep Dashboard...');

        // Check backend health
        const isHealthy = await apiService.healthCheck();
        if (!isHealthy) {
            console.warn('Backend health check failed. The API may not be running.');
        }

        // Initialize map
        mapComponent.init((eventId) => {
            eventPanelComponent.show(eventId);
        });

        // Initialize filters
        filtersComponent.init((filters) => {
            this.loadEvents(filters);
        });

        // Load initial data
        await this.loadEvents();
        await this.loadStats();

        console.log('SitRep Dashboard initialized successfully');
    }

    /**
     * Load events from API and display on map
     */
    async loadEvents(filters = null) {
        this.showLoading();

        try {
            const filterParams = filters || filtersComponent.getFilters();
            const geojson = await apiService.fetchEventsGeoJSON(filterParams);
            
            console.log(`Loaded ${geojson.features.length} events`);
            mapComponent.loadEvents(geojson);

        } catch (error) {
            console.error('Failed to load events:', error);
            alert('Failed to load events. Please check your backend connection.');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Load and display statistics
     */
    async loadStats() {
        try {
            const stats = await apiService.fetchStats(30);
            
            document.getElementById('stat-total').textContent = stats.total_events;
            document.getElementById('stat-high-conf').textContent = stats.high_confidence_count;

        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new SitRepApp();
    app.init();
});
