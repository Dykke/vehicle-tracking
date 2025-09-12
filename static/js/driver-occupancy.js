// Driver Occupancy Controls JavaScript
console.log('🚨 DRIVER OCCUPANCY JS LOADED - Simple occupancy controls');

// Global variables
let currentVehicleId = null;
let vehiclesData = [];

// Load driver vehicle assignment
async function loadDriverVehicleAssignment() {
    try {
        console.log('🚗 Loading driver vehicle assignment...');
        const response = await fetch('/driver/vehicle-assignment');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            vehiclesData = data.vehicles;
            console.log('✅ Vehicle assignment loaded:', vehiclesData);
            
            if (vehiclesData.length > 0) {
                // Auto-select first vehicle
                currentVehicleId = vehiclesData[0].id;
                console.log('🚗 Auto-selecting first vehicle:', currentVehicleId);
                updateVehicleInfo(currentVehicleId);
                updateRouteInfo(currentVehicleId);
            } else {
                console.log('⚠️ No vehicles assigned to driver');
                showToast('Info', 'No vehicles assigned. Contact your operator.', 'info');
            }
        } else {
            console.error('❌ Failed to load vehicle assignment:', data.error);
            showToast('Error', 'Failed to load vehicle assignment', 'error');
        }
    } catch (error) {
        console.error('❌ Error loading vehicle assignment:', error);
        showToast('Error', 'Network error loading vehicle assignment', 'error');
    }
}

// Toast notification function
function showToast(title, message, type = 'info') {
    console.log(`📢 ${title}: ${message} (${type})`);
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#007bff'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 9999;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
        max-width: 300px;
    `;
    toast.innerHTML = `<strong>${title}:</strong> ${message}`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Update vehicle information display
function updateVehicleInfo(vehicleId) {
    const vehicle = vehiclesData.find(v => v.id == vehicleId);
    if (vehicle) {
        const elements = {
            'selectedVehicleReg': vehicle.registration,
            'selectedVehicleType': vehicle.vehicle_type,
            'selectedVehicleStatus': vehicle.status,
            'selectedVehicleOccupancy': vehicle.occupancy_status || 'Unknown'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
        
        const vehicleInfo = document.getElementById('vehicleInfo');
        if (vehicleInfo) vehicleInfo.classList.remove('d-none');
    }
}

// Update route information display
function updateRouteInfo(vehicleId) {
    const vehicle = vehiclesData.find(v => v.id == vehicleId);
    if (vehicle) {
        const routeVehicleName = document.getElementById('routeVehicleName');
        const routeDisplay = document.getElementById('routeDisplay');
        const routeStatus = document.getElementById('routeStatus');
        const routePhase = document.getElementById('routePhase');
        
        if (routeVehicleName) routeVehicleName.textContent = vehicle.registration;
        
        if (vehicle.route && vehicle.route !== 'None' && vehicle.route !== 'null') {
            if (routeDisplay) routeDisplay.textContent = vehicle.route;
            if (routeStatus) {
                routeStatus.textContent = 'Active';
                routeStatus.className = 'badge bg-success';
            }
            
            // Check if there's an active trip for this vehicle
            checkCurrentTripStatus(vehicleId);
        } else {
            if (routeDisplay) routeDisplay.textContent = 'No route set';
            if (routeStatus) {
                routeStatus.textContent = 'No Route';
                routeStatus.className = 'badge bg-secondary';
            }
            // Clear any trip phase display
            if (routePhase) routePhase.textContent = '';
        }
    }
}

// Check current trip status for a vehicle
async function checkCurrentTripStatus(vehicleId) {
    try {
        const response = await fetch(`/driver/current-trip/${vehicleId}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.trip) {
                updateTripPhaseDisplay(data.trip.status);
            }
        }
    } catch (error) {
        console.log('Could not check trip status:', error.message);
    }
}

// Update trip phase display
function updateTripPhaseDisplay(tripStatus) {
    const routePhase = document.getElementById('routePhase');
    if (routePhase) {
        if (tripStatus === 'active') {
            routePhase.textContent = ', Departed';
        } else if (tripStatus === 'completed') {
            routePhase.textContent = ', Arrived';
        } else {
            routePhase.textContent = '';
        }
    }
}

// Update vehicle occupancy status
async function updateOccupancy(status) {
    if (!currentVehicleId) {
        showToast('Error', 'No vehicle selected', 'error');
        return;
    }
    
    try {
        console.log(`🔄 Updating occupancy to: ${status}`);
        
        const response = await fetch(`/driver/vehicle/${currentVehicleId}/occupancy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ occupancy_status: status })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update local vehicle data
            const vehicleIndex = vehiclesData.findIndex(v => v.id == currentVehicleId);
            if (vehicleIndex !== -1) {
                vehiclesData[vehicleIndex].occupancy_status = status;
            }
            
            // Update UI buttons
            updateOccupancyButtons(status);
            
            showToast('Success', `Vehicle marked as ${status}`, 'success');
            console.log('✅ Occupancy updated successfully');
        } else {
            showToast('Error', data.error || 'Failed to update occupancy', 'error');
        }
    } catch (error) {
        console.error('❌ Error updating occupancy:', error);
        showToast('Error', 'Network error updating occupancy', 'error');
    }
}

// Update occupancy button states
function updateOccupancyButtons(status) {
    const vacantBtn = document.getElementById('vacantBtn');
    const fullBtn = document.getElementById('fullBtn');
    
    if (vacantBtn && fullBtn) {
        if (status === 'vacant') {
            vacantBtn.classList.remove('btn-outline-success');
            vacantBtn.classList.add('btn-success');
            fullBtn.classList.remove('btn-danger');
            fullBtn.classList.add('btn-outline-danger');
        } else {
            vacantBtn.classList.remove('btn-success');
            vacantBtn.classList.add('btn-outline-success');
            fullBtn.classList.remove('btn-outline-danger');
            fullBtn.classList.add('btn-danger');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM Content Loaded - Initializing driver occupancy controls');
    console.log('📱 DOM load timestamp:', new Date().toISOString());
    
    // Initialize occupancy buttons
    const vacantBtn = document.getElementById('vacantBtn');
    const fullBtn = document.getElementById('fullBtn');
    
    if (vacantBtn) {
        vacantBtn.addEventListener('click', function() {
            console.log('🔘 Vacant button clicked');
            if (currentVehicleId) {
                updateOccupancy('vacant');
            } else {
                showToast('Error', 'Please select a vehicle first', 'error');
            }
        });
    }
    
    if (fullBtn) {
        fullBtn.addEventListener('click', function() {
            console.log('🔘 Full button clicked');
            if (currentVehicleId) {
                updateOccupancy('full');
            } else {
                showToast('Error', 'Please select a vehicle first', 'error');
            }
        });
    }
    
    // Add keyboard shortcuts for V and F keys
    document.addEventListener('keydown', function(e) {
        if (e.key.toLowerCase() === 'v' && currentVehicleId) {
            e.preventDefault();
            console.log('⌨️ V key pressed - setting vacant');
            updateOccupancy('vacant');
        } else if (e.key.toLowerCase() === 'f' && currentVehicleId) {
            e.preventDefault();
            console.log('⌨️ F key pressed - setting full');
            updateOccupancy('full');
        }
    });
    
    // Load driver vehicle assignment data
    loadDriverVehicleAssignment();
    
    console.log('✅ Driver occupancy controls initialization complete');
});

console.log('✅ Driver occupancy script loaded successfully');
