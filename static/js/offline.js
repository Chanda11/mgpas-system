// static/js/offline.js
class SimpleOfflineManager {
    constructor() {
        this.pendingRequests = JSON.parse(localStorage.getItem('pendingRequests') || '[]');
        this.init();
    }

    init() {
        // Check if we need to sync when coming online
        window.addEventListener('online', () => this.syncPendingRequests());
        
        // Initial sync check
        if (navigator.onLine && this.pendingRequests.length > 0) {
            this.syncPendingRequests();
        }
    }

    async saveRequest(method, url, data) {
        const request = {
            id: Date.now() + Math.random().toString(36).substr(2, 9),
            method,
            url,
            data,
            timestamp: new Date().toISOString()
        };
        
        this.pendingRequests.push(request);
        this.saveToStorage();
        
        return request;
    }

    async syncPendingRequests() {
        if (!navigator.onLine || this.pendingRequests.length === 0) return;
        
        const successfulRequests = [];
        
        for (const request of [...this.pendingRequests]) {
            try {
                const response = await fetch(request.url, {
                    method: request.method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: request.method !== 'GET' ? JSON.stringify(request.data) : null
                });
                
                if (response.ok) {
                    successfulRequests.push(request.id);
                    // Remove from pending requests
                    this.pendingRequests = this.pendingRequests.filter(req => req.id !== request.id);
                }
            } catch (error) {
                console.error('Sync failed for request:', request, error);
            }
        }
        
        this.saveToStorage();
    }

    saveToStorage() {
        localStorage.setItem('pendingRequests', JSON.stringify(this.pendingRequests));
    }

    getCSRFToken() {
        const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }

    getPendingRequestsCount() {
        return this.pendingRequests.length;
    }
}

// Initialize offline manager
const offlineManager = new SimpleOfflineManager();

// Override form submissions to handle offline
document.addEventListener('DOMContentLoaded', function() {
    // Handle student form submissions
    const studentForm = document.getElementById('studentForm');
    if (studentForm) {
        studentForm.addEventListener('submit', async function(e) {
            if (!navigator.onLine) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const formDataObj = Object.fromEntries(formData.entries());
                
                await offlineManager.saveRequest('POST', '/grading/api/students/', formDataObj);
                
                alert('Student data saved offline. It will be synced when you reconnect.');
                this.reset();
            }
        });
    }
});

// Display offline status
function updateOnlineStatus() {
    const offlineAlert = document.getElementById('offlineAlert');
    const pendingCount = offlineManager.getPendingRequestsCount();
    
    if (!navigator.onLine) {
        if (offlineAlert) offlineAlert.style.display = 'block';
        
        // Show pending requests count
        if (pendingCount > 0) {
            const pendingBadge = document.getElementById('pendingRequestsBadge') || 
                                document.createElement('span');
            pendingBadge.id = 'pendingRequestsBadge';
            pendingBadge.className = 'badge bg-warning ms-2';
            pendingBadge.textContent = pendingCount + ' pending';
            
            const offlineText = offlineAlert ? offlineAlert.querySelector('span') : null;
            if (offlineText && !offlineText.querySelector('#pendingRequestsBadge')) {
                offlineText.appendChild(pendingBadge);
            }
        }
    } else {
        if (offlineAlert) offlineAlert.style.display = 'none';
    }
}

// Update status on load and when connectivity changes
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);
updateOnlineStatus();