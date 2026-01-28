/**
 * Filters Component
 * Manages filter sidebar interactions
 */

class FiltersComponent {
    constructor() {
        this.filters = {
            days_back: 30,
            min_confidence: 0.3,
            event_type: '',
            country: ''
        };
        
        this.onFilterChange = null;
    }

    /**
     * Initialize filter controls
     */
    init(onFilterChangeCallback) {
        this.onFilterChange = onFilterChangeCallback;

        // Days filter
        const daysSelect = document.getElementById('filter-days');
        daysSelect.addEventListener('change', (e) => {
            this.filters.days_back = parseInt(e.target.value);
        });

        // Confidence filter
        const confidenceSlider = document.getElementById('filter-confidence');
        const confidenceValue = document.getElementById('confidence-value');
        confidenceSlider.addEventListener('input', (e) => {
            this.filters.min_confidence = parseFloat(e.target.value);
            confidenceValue.textContent = this.filters.min_confidence.toFixed(1);
        });

        // Event type filter
        const eventTypeSelect = document.getElementById('filter-event-type');
        eventTypeSelect.addEventListener('change', (e) => {
            this.filters.event_type = e.target.value;
        });

        // Country filter
        const countryInput = document.getElementById('filter-country');
        countryInput.addEventListener('input', (e) => {
            this.filters.country = e.target.value;
        });

        // Apply filters button
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });

        // Reset filters button
        document.getElementById('reset-filters').addEventListener('click', () => {
            this.resetFilters();
        });
    }

    /**
     * Apply current filters
     */
    applyFilters() {
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }

    /**
     * Reset all filters to defaults
     */
    resetFilters() {
        this.filters = {
            days_back: 30,
            min_confidence: 0.3,
            event_type: '',
            country: ''
        };

        // Update UI
        document.getElementById('filter-days').value = '30';
        document.getElementById('filter-confidence').value = '0.3';
        document.getElementById('confidence-value').textContent = '0.3';
        document.getElementById('filter-event-type').value = '';
        document.getElementById('filter-country').value = '';

        this.applyFilters();
    }

    /**
     * Get current filters
     */
    getFilters() {
        return this.filters;
    }
}

// Export singleton instance
const filtersComponent = new FiltersComponent();
