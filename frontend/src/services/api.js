/**
 * API Service
 * Handles all HTTP requests to the SitRep backend API
 */

const API_BASE_URL = 'http://localhost:8000';

class APIService {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    /**
     * Fetch events as GeoJSON for map display
     */
    async fetchEventsGeoJSON(filters = {}) {
        const params = new URLSearchParams();
        
        if (filters.days_back) params.append('days_back', filters.days_back);
        if (filters.event_type) params.append('event_type', filters.event_type);
        if (filters.min_confidence) params.append('min_confidence', filters.min_confidence);
        if (filters.limit) params.append('limit', filters.limit);

        try {
            const response = await fetch(`${this.baseUrl}/api/events/geojson?${params}`);
            if (!response.ok) throw new Error('Failed to fetch events');
            return await response.json();
        } catch (error) {
            console.error('Error fetching GeoJSON:', error);
            throw error;
        }
    }

    /**
     * Fetch a single event by ID
     */
    async fetchEvent(eventId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/events/${eventId}`);
            if (!response.ok) throw new Error('Event not found');
            return await response.json();
        } catch (error) {
            console.error(`Error fetching event ${eventId}:`, error);
            throw error;
        }
    }

    /**
     * Fetch statistics summary
     */
    async fetchStats(daysBack = 30) {
        try {
            const response = await fetch(`${this.baseUrl}/api/events/stats/summary?days_back=${daysBack}`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            throw error;
        }
    }

    /**
     * Search for events near a location
     */
    async searchNearby(lat, lon, radiusKm = 100) {
        try {
            const params = new URLSearchParams({
                lat: lat,
                lon: lon,
                radius_km: radiusKm
            });
            const response = await fetch(`${this.baseUrl}/api/events/search/nearby?${params}`);
            if (!response.ok) throw new Error('Failed to search nearby events');
            return await response.json();
        } catch (error) {
            console.error('Error searching nearby events:', error);
            throw error;
        }
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

// Export singleton instance
const apiService = new APIService();
