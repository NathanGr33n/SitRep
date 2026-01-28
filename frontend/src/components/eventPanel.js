/**
 * Event Panel Component
 * Displays detailed information about a selected event
 */

class EventPanelComponent {
    constructor() {
        this.panel = document.getElementById('event-panel');
        this.content = document.getElementById('panel-content');
        this.closeButton = document.getElementById('close-panel');
        
        this.closeButton.addEventListener('click', () => this.hide());
    }

    /**
     * Show event details in panel
     */
    async show(eventId) {
        try {
            const event = await apiService.fetchEvent(eventId);
            this.renderEvent(event);
            this.panel.classList.remove('hidden');
        } catch (error) {
            console.error('Failed to load event details:', error);
            this.content.innerHTML = '<p>Failed to load event details.</p>';
            this.panel.classList.remove('hidden');
        }
    }

    /**
     * Hide the panel
     */
    hide() {
        this.panel.classList.add('hidden');
    }

    /**
     * Render event details
     */
    renderEvent(event) {
        const confidenceClass = event.confidence >= 0.7 ? 'confidence-high' :
                                event.confidence >= 0.5 ? 'confidence-medium' : 'confidence-low';
        
        const confidenceLabel = event.confidence >= 0.7 ? 'HIGH' :
                                event.confidence >= 0.5 ? 'MEDIUM' : 'LOW';

        // Format date
        const eventDate = new Date(event.published_date);
        const formattedDate = eventDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        this.content.innerHTML = `
            <h2 class="event-title">${event.event_title}</h2>
            
            <div class="event-meta">
                <div class="meta-item">
                    <span class="meta-label">Event Type</span>
                    <span class="meta-value">${event.event_type}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Date</span>
                    <span class="meta-value">${formattedDate}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Confidence</span>
                    <span class="confidence-badge ${confidenceClass}">
                        ${confidenceLabel} (${(event.confidence * 100).toFixed(0)}%)
                    </span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Location</span>
                    <span class="meta-value">${event.primary_location.name}</span>
                </div>
            </div>

            <div class="event-section">
                <h3>Summary</h3>
                <p>${event.summary}</p>
            </div>

            ${event.analysis ? `
            <div class="event-section">
                <h3>Analysis</h3>
                <p>${event.analysis}</p>
            </div>
            ` : ''}

            ${event.entities && Object.values(event.entities).some(arr => arr.length > 0) ? `
            <div class="event-section">
                <h3>Entities</h3>
                <ul>
                    ${event.entities.organizations && event.entities.organizations.length > 0 ? `
                        <li><strong>Organizations:</strong> ${event.entities.organizations.join(', ')}</li>
                    ` : ''}
                    ${event.entities.locations && event.entities.locations.length > 0 ? `
                        <li><strong>Locations:</strong> ${event.entities.locations.join(', ')}</li>
                    ` : ''}
                    ${event.entities.persons && event.entities.persons.length > 0 ? `
                        <li><strong>Persons:</strong> ${event.entities.persons.join(', ')}</li>
                    ` : ''}
                </ul>
            </div>
            ` : ''}

            ${event.topics && event.topics.length > 0 ? `
            <div class="event-section">
                <h3>Topics</h3>
                <p>${event.topics.join(', ')}</p>
            </div>
            ` : ''}

            ${event.secondary_locations && event.secondary_locations.length > 0 ? `
            <div class="event-section">
                <h3>Related Locations</h3>
                <ul>
                    ${event.secondary_locations.map(loc => `<li>${loc.name}</li>`).join('')}
                </ul>
            </div>
            ` : ''}

            ${event.source_urls && event.source_urls.length > 0 ? `
            <div class="event-section">
                <h3>Sources</h3>
                <ul>
                    ${event.source_urls.map(url => `
                        <li><a href="${url}" target="_blank" class="source-link">${url}</a></li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
        `;
    }
}

// Export singleton instance
const eventPanelComponent = new EventPanelComponent();
