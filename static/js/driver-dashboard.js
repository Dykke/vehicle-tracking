// 🚨 EXTERNAL SCRIPT LOADED - This should appear in console immediately
console.log('🚨 EXTERNAL SCRIPT LOADED - driver-dashboard.js is being executed!');
console.log('🚨 Script loading timestamp:', new Date().toISOString());

// Global variables
let currentVehicleId = null;
let currentTripId = null;
let vehiclesData = [];
let socket = null;
let geolocationWatchId = null;
let isBroadcastingLocation = false;

// Helper function to check if we're on a local network
function isLocalNetwork() {
    return (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname.startsWith('192.168.') ||
        window.location.hostname.startsWith('10.') ||
        window.location.hostname.endsWith('.local')
    );
}

// Update trip counters
async function updateTripCounters() {
    try {
        const response = await fetch('/driver/trip-stats');
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                const todayTripsEl = document.getElementById('todayTripsCount');
                const totalTripsEl = document.getElementById('totalTripsCount');
                
                if (todayTripsEl) {
                    todayTripsEl.textContent = data.stats.today_trips || 0;
                }
                if (totalTripsEl) {
                    totalTripsEl.textContent = data.stats.total_trips || 0;
                }
                
                console.log('✅ Trip counters updated:', data.stats);
            }
        }
    } catch (error) {
        console.error('❌ Error updating trip counters:', error);
        // Fallback: just increment local counters
        const todayTripsEl = document.getElementById('todayTripsCount');
        if (todayTripsEl) {
            const current = parseInt(todayTripsEl.textContent) || 0;
            todayTripsEl.textContent = current + 1;
        }
        const totalTripsEl = document.getElementById('totalTripsCount');
        if (totalTripsEl) {
            const current = parseInt(totalTripsEl.textContent) || 0;
            totalTripsEl.textContent = current + 1;
        }
    }
}
 
function openConfirmationDialog(message, onConfirm) {
    const messageContainer = document.getElementById('confirmationMessage');
    const confirmBtn = document.getElementById('confirmActionBtn');
    const modalEl = document.getElementById('confirmationModal');
    if (!messageContainer || !confirmBtn || !modalEl) {
        const ok = confirm(message || 'Are you sure?');
        if (ok && typeof onConfirm === 'function') onConfirm();
        return;
    }
    messageContainer.textContent = message || 'Are you sure?';
    const modal = new bootstrap.Modal(modalEl);
    const handler = () => {
        try { if (typeof onConfirm === 'function') onConfirm(); } finally {
            confirmBtn.removeEventListener('click', handler);
            modal.hide();
        }
    };
    confirmBtn.addEventListener('click', handler);
    modal.show();
}
 
 // Initialize WebSocket connection
 function initSocket() {
     try {
         socket = io();
         socket.on('connect', function() {
             console.log('✅ Connected to server');
         });
         socket.on('disconnect', function() {
             console.log('❌ Disconnected from server');
         });
     } catch (error) {
         console.error('❌ Socket connection failed:', error);
     }
 }
 
 // Load driver vehicle assignment from API
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
                 enableVehicleControls(); // Enable buttons when vehicle is selected
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
 
 // Toast notification function is now globally available from base.html
 // No need to redefine it here - it's inherited from the base template
 
 // Enable vehicle controls
 function enableVehicleControls() {
     console.log('🔧 Enabling vehicle controls...');
     const buttons = ['routeDetailsBtn', 'routeChangeBtn', 'departureBtn', 'arrivalBtn'];
     buttons.forEach(btnId => {
         const btn = document.getElementById(btnId);
         if (btn) {
             btn.disabled = false;
             console.log(`✅ Enabled button: ${btnId}`);
         } else {
             console.log(`⚠️ Button not found: ${btnId}`);
         }
     });
 }
 
 // Fetch fresh vehicle data from backend
 async function fetchFreshVehicleData() {
     if (!currentVehicleId) {
         console.log('⚠️ No vehicle selected for data refresh');
         return;
     }
     
     try {
         console.log('🔄 Fetching fresh vehicle data...');
         
         const response = await fetch(`/driver/vehicle/${currentVehicleId}/details`);
         
         if (!response.ok) {
             throw new Error(`HTTP ${response.status}: ${response.statusText}`);
         }
         
         const data = await response.json();
         
         if (data.success) {
             // Update local vehicle data
             const vehicleIndex = vehiclesData.findIndex(v => v.id == currentVehicleId);
             if (vehicleIndex !== -1) {
                 vehiclesData[vehicleIndex] = { ...vehiclesData[vehicleIndex], ...data.vehicle };
             }
             
             // Update UI with fresh data
             updateRouteInfo(currentVehicleId);
             updateOccupancyButtons(data.vehicle.occupancy_status || 'Unknown');
             
             console.log('✅ Vehicle data refreshed successfully');
             showToast('Success', 'Vehicle data updated', 'success');
         } else {
             console.log('⚠️ Failed to refresh vehicle data:', data.error);
         }
     } catch (error) {
         console.error('❌ Error fetching fresh vehicle data:', error);
         showToast('Error', 'Failed to refresh vehicle data', 'error');
     }
 }
 
 // Update vehicle information display
 function updateVehicleInfo(vehicleId) {
     const vehicle = vehiclesData.find(v => v.id == vehicleId);
     if (vehicle) {
         // Log vehicle details to console for debugging
         console.log('🚗 Current Vehicle Details:', {
             id: vehicle.id,
             registration: vehicle.registration_number,
             type: vehicle.vehicle_type,
             status: vehicle.status,
             occupancy: vehicle.occupancy_status || 'Unknown',
             route: vehicle.route || 'None'
         });
         
         // Update route info which is still displayed in the UI
         updateRouteInfo(vehicleId);
     }
 }
 
   // Update route information display
  function updateRouteInfo(vehicleId) {
      const vehicle = vehiclesData.find(v => v.id == vehicleId);
      if (vehicle) {
          document.getElementById('routeVehicleName').textContent = vehicle.registration_number;
          
          if (vehicle.route && vehicle.route !== 'None' && vehicle.route !== 'null') {
              // Try to parse route info for better display
              let routeDisplay = vehicle.route;
              if (vehicle.route_info) {
                  try {
                      const routeInfo = JSON.parse(vehicle.route_info);
                      if (routeInfo.origin && routeInfo.destination) {
                          routeDisplay = `${routeInfo.origin} → ${routeInfo.destination}`;
                      }
                  } catch (e) {
                      // If parsing fails, use the route name as is
                      console.log('Could not parse route info, using route name');
                  }
              }
              
              document.getElementById('routeDisplay').textContent = routeDisplay;
              document.getElementById('routeStatus').textContent = 'Active';
              document.getElementById('routeStatus').className = 'badge bg-success';
              enableVehicleControls();
              
              // Check if there's an active trip for this vehicle
              checkCurrentTripStatus(vehicleId);
          } else {
              document.getElementById('routeDisplay').textContent = 'No route set';
              document.getElementById('routeStatus').textContent = 'No Route';
              document.getElementById('routeStatus').className = 'badge bg-secondary';
              // Still enable controls even without route
              enableVehicleControls();
              
              // Clear any trip phase display
              const routePhase = document.getElementById('routePhase');
              if (routePhase) routePhase.textContent = '';
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

// Location broadcasting helpers
async function postVehicleLocation(latitude, longitude, accuracy) {
    try {
        const response = await fetch(`/driver/vehicle/${currentVehicleId}/location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude, accuracy })
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Failed to post location:', error);
        return null;
    }
}

function startLocationBroadcasting() {
    if (isBroadcastingLocation) return;
    if (!('geolocation' in navigator)) {
        showToast('Error', 'Geolocation not supported on this device', 'error');
        return;
    }
    
    // Check for secure context
    if (location.protocol !== 'https:' && !isLocalNetwork()) {
        showToast('Security Warning', 'Geolocation requires HTTPS or local network access. Try localhost:5000 instead.', 'error');
        return;
    }
    
    isBroadcastingLocation = true;
    showToast('Tracking', 'Location tracking started', 'info');
    geolocationWatchId = navigator.geolocation.watchPosition(
        async (pos) => {
            if (!currentVehicleId) return;
            const { latitude, longitude, accuracy } = pos.coords;
            await postVehicleLocation(latitude, longitude, accuracy);
        },
        (err) => {
            console.error('❌ Geolocation error:', err);
            let errorMsg = 'Location permission denied or unavailable';
            if (err.code === 1) {
                if (err.message.includes('secure origins')) {
                    errorMsg = 'Geolocation requires HTTPS. Try accessing via localhost:5000 instead of IP address, or use a secure connection.';
                } else {
                    errorMsg = 'Location permission denied. Please allow location access in your browser settings.';
                }
            } else if (err.code === 2) {
                errorMsg = 'Location unavailable. Check your GPS/network connection.';
            } else if (err.code === 3) {
                errorMsg = 'Location request timed out. Please try again.';
            }
            showToast('Location Error', errorMsg, 'error');
        },
        {
            enableHighAccuracy: true,
            maximumAge: 5000,
            timeout: 15000
        }
    );
}

function stopLocationBroadcasting() {
    if (geolocationWatchId !== null) {
        try { navigator.geolocation.clearWatch(geolocationWatchId); } catch (_) {}
        geolocationWatchId = null;
    }
    if (isBroadcastingLocation) {
        isBroadcastingLocation = false;
        showToast('Tracking', 'Location tracking stopped', 'info');
    }
}
 
 // Start trip
 async function startTrip() {
     if (!currentVehicleId) {
         showToast('Error', 'No vehicle selected', 'error');
         return;
     }
     
     const vehicle = vehiclesData.find(v => v.id == currentVehicleId);
     if (!vehicle || !vehicle.route) {
         showToast('Error', 'No route assigned. Please contact your operator.', 'error');
         return;
     }
     
     try {
         const response = await fetch('/driver/trip/start', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 vehicle_id: currentVehicleId,
                 route_name: vehicle.route
             })
         });
         
         if (!response.ok) {
             let serverMsg = '';
             try { const errData = await response.json(); serverMsg = errData.error || ''; } catch (_) {}
             if (response.status === 400 && serverMsg.toLowerCase().includes('active trip')) {
                 openConfirmationDialog('There is already an active trip for this vehicle. End it now and start a new one?', async () => {
                     await endTrip();
                     await startTrip();
                 });
                 return;
             }
             throw new Error(`HTTP ${response.status}: ${response.statusText}${serverMsg ? ' - ' + serverMsg : ''}`);
         }
         
         const data = await response.json();
         
         if (data.success) {
            currentTripId = data.trip.id;
            showTripManagement();
            showToast('Success', 'Trip started successfully', 'success');
            console.log('✅ Trip started:', data.trip);
            startLocationBroadcasting();
            updateTripPhaseDisplay('active');
            
            // Update trip counter
            updateTripCounters();
         } else {
             showToast('Error', data.error || 'Failed to start trip', 'error');
         }
     } catch (error) {
         console.error('❌ Error starting trip:', error);
         showToast('Error', 'Network error starting trip', 'error');
     }
 }
 
 // End trip
 async function endTrip() {
     if (!currentVehicleId) {
         showToast('Error', 'No vehicle selected', 'error');
         return;
     }
     
     try {
         const response = await fetch('/driver/trip/end', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({ vehicle_id: currentVehicleId })
         });
         
         if (!response.ok) {
             throw new Error(`HTTP ${response.status}: ${response.statusText}`);
         }
         
         const data = await response.json();
         
         if (data.success) {
            currentTripId = null;
            hideTripManagement();
            showToast('Success', 'Trip ended successfully', 'success');
            console.log('✅ Trip ended:', data.trip);
            stopLocationBroadcasting();
            updateTripPhaseDisplay('completed');
            
            // Update trip counter
            updateTripCounters();
         } else {
             showToast('Error', data.error || 'Failed to end trip', 'error');
         }
     } catch (error) {
         console.error('❌ Error ending trip:', error);
         showToast('Error', 'Network error ending trip', 'error');
     }
 }
 
 // Show/hide trip management (simplified - no UI elements to toggle)
function showTripManagement() {
    console.log('✅ Trip management activated');
}

function hideTripManagement() {
    console.log('✅ Trip management deactivated');
}
 
 // Route functions
 function showRouteDetails() {
     if (!currentVehicleId) {
         showToast('Error', 'No vehicle selected', 'error');
         return;
     }
     
     const vehicle = vehiclesData.find(v => v.id == currentVehicleId);
     if (vehicle && vehicle.route) {
         document.getElementById('modalRouteVehicle').textContent = vehicle.registration_number;
         document.getElementById('modalRouteName').textContent = vehicle.route;
         document.getElementById('modalRouteStart').textContent = 'Starting point';
         document.getElementById('modalRouteEnd').textContent = 'Destination';
         document.getElementById('modalRouteDistance').textContent = 'Calculated';
         document.getElementById('modalRouteETA').textContent = 'Estimated';

         const modal = new bootstrap.Modal(document.getElementById('routeDetailsModal'));
         modal.show();
     } else {
         showToast('Error', 'No route information available', 'error');
     }
 }
 
   function requestRouteChange() {
      if (!currentVehicleId) {
          showToast('Error', 'No vehicle selected', 'error');
          return;
      }
      
      // Show the route change modal
      const modal = new bootstrap.Modal(document.getElementById('routeChangeModal'));
      modal.show();
  }
 
 function departure() {
     if (!currentVehicleId) {
         showToast('Error', 'No vehicle selected', 'error');
         return;
     }
     
     const vehicle = vehiclesData.find(v => v.id == currentVehicleId);
     if (!vehicle || !vehicle.route) {
         showToast('Error', 'No route assigned. Please contact your operator.', 'error');
         return;
     }
     
     startTrip();
 }
 
   function arrival() {
      if (!currentVehicleId) {
          showToast('Error', 'No vehicle selected', 'error');
          return;
      }
      
      endTrip();
  }
  
  // Route change functionality
  async function changeVehicleRoute() {
      if (!currentVehicleId) {
          showToast('Error', 'No vehicle selected', 'error');
          return;
      }
      
      const routeName = document.getElementById('newRouteName').value.trim();
      const startLocation = document.getElementById('startLocation').value.trim();
      const endLocation = document.getElementById('endLocation').value.trim();
      
      if (!routeName || !startLocation || !endLocation) {
          showToast('Error', 'Please fill in all route fields', 'error');
          return;
      }
      
      try {
          console.log(`🔄 Changing route to: ${routeName}`);
          
          const response = await fetch(`/driver/vehicle/${currentVehicleId}/route`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                  route_name: routeName,
                  start_location: startLocation,
                  end_location: endLocation
              })
          });
          
          if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          const data = await response.json();
          
          if (data.success) {
              // Update local vehicle data
              const vehicleIndex = vehiclesData.findIndex(v => v.id == currentVehicleId);
              if (vehicleIndex !== -1) {
                  vehiclesData[vehicleIndex].route = routeName;
                  vehiclesData[vehicleIndex].route_info = JSON.stringify({
                      origin: startLocation,
                      destination: endLocation
                  });
              }
              
              // Update UI
              updateRouteInfo(currentVehicleId);
              
              // Close modal
              const modal = bootstrap.Modal.getInstance(document.getElementById('routeChangeModal'));
              modal.hide();
              
              // Clear form
              document.getElementById('routeChangeForm').reset();
              
              showToast('Success', 'Route changed successfully', 'success');
              console.log('✅ Route changed successfully');
          } else {
              showToast('Error', data.error || 'Failed to change route', 'error');
          }
      } catch (error) {
          console.error('❌ Error changing route:', error);
          showToast('Error', 'Network error changing route', 'error');
      }
  }
 
          // Utility functions
 function refreshVehicleData() {
     console.log('🔄 Refreshing vehicle data...');
     loadDriverVehicleAssignment();
 }
 
 
 
 // Passenger management functions
 async function recordPassengerEvent(eventType) {
     if (!currentVehicleId || !currentTripId) {
         showToast('Error', 'No active trip. Start a trip first.', 'error');
         return;
     }
     
     const count = parseInt(document.getElementById('passengerCount').value) || 1;
     
     try {
         const response = await fetch('/driver/passenger', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 vehicle_id: currentVehicleId,
                 event_type: eventType,
                 count: count
             })
         });
         
         if (!response.ok) {
             throw new Error(`HTTP ${response.status}: ${response.statusText}`);
         }
         
         const data = await response.json();
         
         if (data.success) {
             showToast('Success', `${eventType} event recorded`, 'success');
             updateTripSummary();
         } else {
             showToast('Error', data.error || 'Failed to record event', 'error');
         }
     } catch (error) {
         console.error('❌ Error recording passenger event:', error);
         showToast('Error', 'Network error recording event', 'error');
     }
 }
 
 async function updateTripSummary() {
     if (!currentVehicleId) return;
     
     try {
         const response = await fetch(`/driver/current-trip/${currentVehicleId}`);
         if (response.ok) {
             const data = await response.json();
             if (data.success && data.trip) {
                 const summary = data.trip.passenger_summary;
                 document.getElementById('tripBoarded').textContent = summary.boards;
                 document.getElementById('tripAlighted').textContent = summary.alights;
                 document.getElementById('tripCurrent').textContent = summary.current_passengers;
             }
         }
     } catch (error) {
         console.error('❌ Error updating trip summary:', error);
     }
 }
 
     // Event delegation system
 function setupEventDelegation() {
     console.log('🔧 Setting up event delegation...');
     
     document.addEventListener('click', function(e) {
         console.log('🔍 Click detected on:', e.target);
         console.log('🔍 Click target tagName:', e.target.tagName);
         console.log('🔍 Click target className:', e.target.className);
         console.log('🔍 Click target has data-action:', e.target.hasAttribute('data-action'));
         
         // Check if the clicked element or any of its parents has data-action
         let element = e.target;
         let action = null;
         
         while (element && element !== document.body) {
             if (element.hasAttribute('data-action')) {
                 action = element.getAttribute('data-action');
                 console.log('🔘 Found data-action on element:', element.tagName, 'Action:', action);
                 break;
             }
             element = element.parentElement;
         }
         
         if (action) {
             console.log('🔘 Button clicked:', action);
             
                           try {
                  switch(action) {
                      case 'refreshVehicleData':
                          refreshVehicleData();
                          break;
                      case 'showRouteDetails':
                          showRouteDetails();
                          break;
                      case 'requestRouteChange':
                          requestRouteChange();
                          break;
                      case 'departure':
                          departure();
                          break;
                      case 'arrival':
                          arrival();
                          break;
                      default:
                          console.log('⚠️ Unknown action:', action);
                  }
             } catch (error) {
                 console.error('❌ ERROR calling function:', error);
                 showToast('Error', 'Function execution failed', 'error');
             }
         } else {
             console.log('⚠️ No data-action found on clicked element or its parents');
         }
     });
     
     console.log('✅ Event delegation setup complete');
 }
 
     // Initialize when DOM is loaded
 document.addEventListener('DOMContentLoaded', function() {
     console.log('📱 DOM Content Loaded - Initializing driver dashboard');
     console.log('📱 DOM load timestamp:', new Date().toISOString());
     console.log('Driver dashboard script loaded');
     
     // Initialize WebSocket connection
     initSocket();
     
     // Setup event delegation for buttons
     setupEventDelegation();
     
     // Add direct event listeners to departure and arrival buttons for debugging
     const departureBtn = document.getElementById('departureBtn');
     const arrivalBtn = document.getElementById('arrivalBtn');
     
     if (departureBtn) {
         console.log('✅ Departure button found, adding direct listener');
         departureBtn.addEventListener('click', function(e) {
             console.log('🔘 Direct departure button click detected');
             e.preventDefault();
             e.stopPropagation();
             departure();
         });
     } else {
         console.log('❌ Departure button not found');
     }
     
     if (arrivalBtn) {
         console.log('✅ Arrival button found, adding direct listener');
         arrivalBtn.addEventListener('click', function(e) {
             console.log('🔘 Direct arrival button click detected');
             e.preventDefault();
             e.stopPropagation();
             arrival();
         });
     } else {
         console.log('❌ Arrival button not found');
     }
     
     // Initialize occupancy buttons
     const vacantBtn = document.getElementById('vacantBtn');
     const fullBtn = document.getElementById('fullBtn');
     
     if (vacantBtn) {
         vacantBtn.addEventListener('click', function() {
             if (currentVehicleId) {
                 updateOccupancy('vacant');
             } else {
                 showToast('Error', 'Please select a vehicle first', 'error');
             }
         });
     }
     
     if (fullBtn) {
         fullBtn.addEventListener('click', function() {
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
     
     // Initialize passenger management buttons
     const increaseBtn = document.getElementById('increaseBtn');
     const decreaseBtn = document.getElementById('decreaseBtn');
     const boardBtn = document.getElementById('boardBtn');
     const alightBtn = document.getElementById('alightBtn');
     const endTripBtn = document.getElementById('endTripBtn');
     
     if (increaseBtn) {
         increaseBtn.addEventListener('click', function() {
             const countInput = document.getElementById('passengerCount');
             countInput.value = parseInt(countInput.value) + 1;
         });
     }
     
     if (decreaseBtn) {
         decreaseBtn.addEventListener('click', function() {
             const countInput = document.getElementById('passengerCount');
             const currentValue = parseInt(countInput.value);
             if (currentValue > 1) {
                 countInput.value = currentValue - 1;
             }
         });
     }
     
     if (boardBtn) {
         boardBtn.addEventListener('click', function() {
             recordPassengerEvent('board');
         });
     }
     
     if (alightBtn) {
         alightBtn.addEventListener('click', function() {
             recordPassengerEvent('alight');
         });
     }
     
     if (endTripBtn) {
         endTripBtn.addEventListener('click', function() {
             endTrip();
         });
     }
     
                     // Load driver vehicle assignment data
     loadDriverVehicleAssignment();
     
     // Load initial trip counters
     updateTripCounters();
     
     // Add route change confirmation button listener
      const confirmRouteChangeBtn = document.getElementById('confirmRouteChange');
      if (confirmRouteChangeBtn) {
          confirmRouteChangeBtn.addEventListener('click', function() {
              changeVehicleRoute();
          });
      }
      
      console.log('✅ Driver dashboard initialization complete');
  });
 
 console.log('✅ Driver dashboard script loaded successfully');
 
 // Test function to verify JavaScript is working
 function testJavaScript() {
     console.log('🧪 JavaScript test function called successfully');
     alert('JavaScript is working!');
 }

// Default route definitions with coordinates
const DEFAULT_ROUTES = {
    'brookes-point-to-puerto-princesa': {
        name: "Brooke's Point to Puerto Princesa",
        start: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" },
        end: { lat: 9.7406, lng: 118.7397, name: "Puerto Princesa, Palawan, Philippines" }
    },
    'puerto-princesa-to-brookes-point': {
        name: "Puerto Princesa to Brooke's Point",
        start: { lat: 9.7406, lng: 118.7397, name: "Puerto Princesa, Palawan, Philippines" },
        end: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" }
    },
    'brookes-point-to-bataraza': {
        name: "Brooke's Point to Bataraza",
        start: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" },
        end: { lat: 8.6737, lng: 117.6544, name: "Bataraza, Palawan, Philippines" }
    },
    'bataraza-to-brookes-point': {
        name: "Bataraza to Brooke's Point",
        start: { lat: 8.6737, lng: 117.6544, name: "Bataraza, Palawan, Philippines" },
        end: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" }
    },
    'rio-tuba-to-brookes-point': {
        name: "Rio Tuba to Brooke's Point",
        start: { lat: 8.6737, lng: 117.6544, name: "Rio Tuba, Palawan, Philippines" },
        end: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" }
    },
    'brookes-point-to-rio-tuba': {
        name: "Brooke's Point to Rio Tuba",
        start: { lat: 8.7979, lng: 117.8302, name: "Brooke's Point, Palawan, Philippines" },
        end: { lat: 8.6737, lng: 117.6544, name: "Rio Tuba, Palawan, Philippines" }
    }
};

// Function to handle default route selection
function handleDefaultRouteSelection() {
    const selectElement = document.getElementById('default-route-select');
    const selectedValue = selectElement.value;
    
    if (!selectedValue) {
        return; // No route selected
    }
    
    const routeData = DEFAULT_ROUTES[selectedValue];
    if (!routeData) {
        console.error('Unknown route selected:', selectedValue);
        return;
    }
    
    console.log('Default route selected:', routeData);
    
    // Update the form fields with the default route data
    const routeNameInput = document.getElementById('newRouteName');
    const startLocationInput = document.getElementById('startLocation');
    const endLocationInput = document.getElementById('endLocation');
    
    if (routeNameInput) routeNameInput.value = routeData.name;
    if (startLocationInput) startLocationInput.value = routeData.start.name;
    if (endLocationInput) endLocationInput.value = routeData.end.name;
    
    // Show success message
    showToast('Route Set', `Default route "${routeData.name}" has been selected`, 'success');
}