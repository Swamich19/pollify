// Global JavaScript for Pollify

// Initialize Socket.IO connection
let socket;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO if available
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Copy to clipboard functionality
    window.copyToClipboard = function(text, successMessage = 'Copied to clipboard!') {
        navigator.clipboard.writeText(text).then(function() {
            showToast(successMessage);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
            showToast('Failed to copy to clipboard', 'error');
        });
    };
    
    // Toast notification system
    window.showToast = function(message, type = 'success') {
        const toastContainer = getOrCreateToastContainer();
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i data-feather="${type === 'error' ? 'alert-circle' : 'check-circle'}" class="me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        // Replace feather icons
        feather.replace();
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove toast element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastContainer.removeChild(toastEl);
        });
    };
    
    function getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }
    
    // Form validation helpers
    window.validateForm = function(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;
        
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        
        inputs.forEach(function(input) {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    };
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Utility functions for polls
window.PollUtils = {
    // Join a poll room for real-time updates
    joinPollRoom: function(pollId) {
        if (socket) {
            socket.emit('join_poll', {poll_id: pollId});
        }
    },
    
    // Leave a poll room
    leavePollRoom: function(pollId) {
        if (socket) {
            socket.emit('leave_poll', {poll_id: pollId});
        }
    },
    
    // Format numbers with commas
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    // Calculate percentage
    calculatePercentage: function(part, total) {
        if (total === 0) return 0;
        return Math.round((part / total) * 100);
    },
    
    // Generate random colors for charts
    generateColors: function(count) {
        const colors = [
            '#0d6efd', '#198754', '#ffc107', '#dc3545',
            '#6610f2', '#fd7e14', '#20c997', '#6f42c1',
            '#f8f9fa', '#6c757d', '#343a40', '#495057'
        ];
        
        const result = [];
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        return result;
    }
};

// Error handling for failed requests
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred. Please try again.', 'error');
});

// Handle online/offline status
window.addEventListener('online', function() {
    showToast('Connection restored!');
});

window.addEventListener('offline', function() {
    showToast('You are currently offline. Some features may not work.', 'error');
});
