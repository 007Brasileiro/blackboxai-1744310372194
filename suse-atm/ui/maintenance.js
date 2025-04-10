// © 2024 Banco do Brasil
// Developed by A1051594 - Aprendiz do Banco do Brasil
// All rights reserved.

// Global state
let currentStatus = {
    atmId: null,
    errorDetails: null,
    diagnosticResults: null,
    maintenanceHistory: [],
    lastUpdate: null
};

// Configuration
const CONFIG = {
    updateInterval: 5000, // 5 seconds
    endpoints: {
        status: '/api/status',
        repair: '/api/repair',
        technician: '/api/technician',
        shutdown: '/api/shutdown'
    }
};

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    initializePage();
    // Start periodic updates
    setInterval(refreshStatus, CONFIG.updateInterval);
});

async function initializePage() {
    try {
        await refreshStatus();
        setupEventListeners();
        updateTimestamp();
    } catch (error) {
        console.error('Failed to initialize page:', error);
        showError('Failed to initialize maintenance interface');
    }
}

async function refreshStatus() {
    try {
        const response = await fetch(CONFIG.endpoints.status);
        const data = await response.json();
        
        updateStatus(data);
        updateDiagnostics(data.diagnostics);
        updateMaintenanceHistory(data.history);
        updateStatusUpdates(data.updates);
        
        currentStatus = { ...data };
        updateTimestamp();
    } catch (error) {
        console.error('Failed to refresh status:', error);
        showError('Failed to update status');
    }
}

function updateStatus(data) {
    const errorDetails = document.getElementById('error-details');
    if (!errorDetails) return;

    // Update ATM ID
    document.getElementById('atm-id').textContent = `ATM ID: ${data.atmId}`;

    // Clear loading state
    errorDetails.innerHTML = '';

    // Create error details content
    const content = document.createElement('div');
    content.innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center">
                <span class="font-semibold">Error Type:</span>
                <span class="ml-2 ${getErrorTypeClass(data.errorType)}">${data.errorType}</span>
            </div>
            <div class="flex items-center">
                <span class="font-semibold">Component:</span>
                <span class="ml-2">${data.component}</span>
            </div>
            <div class="mt-2">
                <span class="font-semibold">Description:</span>
                <p class="mt-1 text-gray-600">${data.description}</p>
            </div>
        </div>
    `;
    
    errorDetails.appendChild(content);
}

function updateDiagnostics(diagnostics) {
    const diagnosticDetails = document.getElementById('diagnostic-details');
    if (!diagnosticDetails) return;

    // Clear loading state
    diagnosticDetails.innerHTML = '';

    // Create diagnostics content
    const content = document.createElement('div');
    content.innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center">
                <span class="font-semibold">AI Analysis:</span>
                <span class="ml-2">${diagnostics.analysis}</span>
            </div>
            <div class="flex items-center">
                <span class="font-semibold">Confidence:</span>
                <span class="ml-2">${diagnostics.confidence}%</span>
            </div>
            <div class="mt-2">
                <span class="font-semibold">Recommended Action:</span>
                <p class="mt-1 text-gray-600">${diagnostics.recommendation}</p>
            </div>
        </div>
    `;
    
    diagnosticDetails.appendChild(content);
}

function updateMaintenanceHistory(history) {
    const maintenanceHistory = document.getElementById('maintenance-history');
    if (!maintenanceHistory) return;

    // Clear loading state
    maintenanceHistory.innerHTML = '';

    // Create history content
    const content = document.createElement('div');
    content.innerHTML = history.map(entry => `
        <div class="border-b border-gray-200 py-2 last:border-0">
            <div class="flex justify-between items-center">
                <span class="font-semibold">${entry.timestamp}</span>
                <span class="${getStatusClass(entry.status)}">${entry.status}</span>
            </div>
            <p class="text-sm text-gray-600 mt-1">${entry.action}</p>
        </div>
    `).join('');
    
    maintenanceHistory.appendChild(content);
}

function updateStatusUpdates(updates) {
    const statusUpdates = document.getElementById('status-updates');
    if (!statusUpdates) return;

    // Clear loading state
    statusUpdates.innerHTML = '';

    // Create updates content
    const content = document.createElement('div');
    content.innerHTML = updates.map(update => `
        <div class="flex items-center space-x-2 py-2">
            <i class="${getUpdateIcon(update.type)} text-${getUpdateColor(update.type)}"></i>
            <span class="text-gray-700">${update.message}</span>
            <span class="text-gray-400 text-sm">${update.timestamp}</span>
        </div>
    `).join('');
    
    statusUpdates.appendChild(content);
}

async function attemptRepair() {
    try {
        const response = await fetch(CONFIG.endpoints.repair, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ atmId: currentStatus.atmId })
        });

        const result = await response.json();
        if (result.success) {
            showSuccess('Repair attempt initiated');
            await refreshStatus();
        } else {
            showError('Repair attempt failed');
        }
    } catch (error) {
        console.error('Failed to attempt repair:', error);
        showError('Failed to initiate repair');
    }
}

async function requestTechnician() {
    try {
        const response = await fetch(CONFIG.endpoints.technician, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                atmId: currentStatus.atmId,
                errorDetails: currentStatus.errorDetails
            })
        });

        const result = await response.json();
        if (result.success) {
            showSuccess('Technician request submitted');
        } else {
            showError('Failed to request technician');
        }
    } catch (error) {
        console.error('Failed to request technician:', error);
        showError('Failed to submit technician request');
    }
}

async function shutdownATM() {
    if (!confirm('Are you sure you want to initiate emergency shutdown?')) {
        return;
    }

    try {
        const response = await fetch(CONFIG.endpoints.shutdown, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ atmId: currentStatus.atmId })
        });

        const result = await response.json();
        if (result.success) {
            showSuccess('Emergency shutdown initiated');
            // Disable all controls
            disableControls();
        } else {
            showError('Failed to initiate shutdown');
        }
    } catch (error) {
        console.error('Failed to shutdown ATM:', error);
        showError('Failed to initiate shutdown');
    }
}

// Utility functions
function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    if (timestamp) {
        timestamp.textContent = `Last Updated: ${new Date().toLocaleTimeString()}`;
    }
}

function getErrorTypeClass(errorType) {
    const classes = {
        'CRITICAL': 'text-red-600',
        'WARNING': 'text-yellow-600',
        'INFO': 'text-blue-600'
    };
    return classes[errorType] || 'text-gray-600';
}

function getStatusClass(status) {
    const classes = {
        'SUCCESS': 'text-green-600',
        'FAILED': 'text-red-600',
        'IN_PROGRESS': 'text-yellow-600'
    };
    return classes[status] || 'text-gray-600';
}

function getUpdateIcon(type) {
    const icons = {
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle',
        'success': 'fas fa-check-circle'
    };
    return icons[type] || 'fas fa-info-circle';
}

function getUpdateColor(type) {
    const colors = {
        'error': 'red-500',
        'warning': 'yellow-500',
        'info': 'blue-500',
        'success': 'green-500'
    };
    return colors[type] || 'gray-500';
}

function showError(message) {
    // Implement error notification
    console.error(message);
}

function showSuccess(message) {
    // Implement success notification
    console.log(message);
}

function disableControls() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = true;
        button.classList.add('opacity-50', 'cursor-not-allowed');
    });
}

function setupEventListeners() {
    // Add any additional event listeners here
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            refreshStatus();
        }
    });
}
