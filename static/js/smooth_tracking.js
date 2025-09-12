/**
 * Smooth Vehicle Tracking Module
 * 
 * This module provides functions for smoothly updating vehicle positions on a map,
 * including position prediction for low-signal situations.
 */

// Configuration
const ANIMATION_DURATION = 1000; // milliseconds for position animation
const PREDICTION_INTERVAL = 1000; // milliseconds between position predictions
const MAX_PREDICTION_TIME = 30000; // maximum time to predict positions (30 seconds)
const FADE_START_TIME = 10000; // time when marker starts fading (10 seconds)

// Track vehicle data for predictions
const vehicleData = {};

/**
 * Update a vehicle's position with smooth animation
 * 
 * @param {Object} marker - The Leaflet marker object
 * @param {Array} newPosition - [latitude, longitude]
 * @param {Number} speed - Speed in km/h
 */
function updateVehiclePosition(marker, newPosition, speed) {
    if (!marker) return;
    
    const vehicleId = getVehicleIdFromMarker(marker);
    const currentTime = Date.now();
    const currentPosition = marker.getLatLng();
    
    // Store vehicle data for predictions
    if (!vehicleData[vehicleId]) {
        vehicleData[vehicleId] = {
            lastPosition: [currentPosition.lat, currentPosition.lng],
            lastUpdateTime: currentTime,
            speed: speed,
            heading: 0,
            predictionInterval: null,
            lastPredictionTime: 0
        };
    } else {
        // Calculate heading based on previous and new position
        const lastPos = vehicleData[vehicleId].lastPosition;
        vehicleData[vehicleId].heading = calculateHeading(
            lastPos[0], lastPos[1], 
            newPosition[0], newPosition[1]
        );
        
        // Update stored data
        vehicleData[vehicleId].lastPosition = newPosition;
        vehicleData[vehicleId].lastUpdateTime = currentTime;
        vehicleData[vehicleId].speed = speed;
        
        // Reset prediction state
        if (vehicleData[vehicleId].predictionInterval) {
            clearInterval(vehicleData[vehicleId].predictionInterval);
            vehicleData[vehicleId].predictionInterval = null;
        }
        
        // Reset marker opacity
        updateMarkerOpacity(marker, 1.0);
    }
    
    // Animate the marker to the new position
    marker.setLatLng(newPosition);
    
    // Start position prediction for low-signal situations
    startPositionPrediction(vehicleId, marker);
}

/**
 * Start predicting vehicle positions when updates are not received
 * 
 * @param {String|Number} vehicleId - The vehicle ID
 * @param {Object} marker - The Leaflet marker object
 */
function startPositionPrediction(vehicleId, marker) {
    if (!vehicleData[vehicleId]) return;
    
    // Clear any existing prediction interval
    if (vehicleData[vehicleId].predictionInterval) {
        clearInterval(vehicleData[vehicleId].predictionInterval);
    }
    
    // Set up a new prediction interval
    vehicleData[vehicleId].predictionInterval = setInterval(() => {
        const currentTime = Date.now();
        const timeSinceUpdate = currentTime - vehicleData[vehicleId].lastUpdateTime;
        
        // Stop predicting after maximum time
        if (timeSinceUpdate > MAX_PREDICTION_TIME) {
            clearInterval(vehicleData[vehicleId].predictionInterval);
            vehicleData[vehicleId].predictionInterval = null;
            return;
        }
        
        // Predict the new position
        const predictedPosition = predictPosition(vehicleId, timeSinceUpdate);
        if (predictedPosition) {
            marker.setLatLng(predictedPosition);
            
            // Gradually reduce opacity as predictions continue
            const opacity = calculateOpacity(timeSinceUpdate);
            updateMarkerOpacity(marker, opacity);
        }
        
        vehicleData[vehicleId].lastPredictionTime = currentTime;
    }, PREDICTION_INTERVAL);
}

/**
 * Predict a vehicle's position based on its speed and heading
 * 
 * @param {String|Number} vehicleId - The vehicle ID
 * @param {Number} timeSinceUpdate - Time in milliseconds since last real update
 * @returns {Array|null} - [latitude, longitude] or null if prediction not possible
 */
function predictPosition(vehicleId, timeSinceUpdate) {
    const data = vehicleData[vehicleId];
    if (!data || data.speed <= 0) return null;
    
    // Convert speed from km/h to meters per millisecond
    const speedMps = (data.speed * 1000) / 3600000;
    
    // Calculate distance traveled since last update
    const distance = speedMps * timeSinceUpdate;
    
    // Calculate new position based on heading
    const lastPos = data.lastPosition;
    const heading = data.heading;
    
    // Convert heading (degrees) to radians
    const headingRad = (heading * Math.PI) / 180;
    
    // Earth radius in meters
    const R = 6371000;
    
    // Convert latitude and longitude to radians
    const lat1 = (lastPos[0] * Math.PI) / 180;
    const lon1 = (lastPos[1] * Math.PI) / 180;
    
    // Calculate new latitude
    const lat2 = Math.asin(
        Math.sin(lat1) * Math.cos(distance / R) +
        Math.cos(lat1) * Math.sin(distance / R) * Math.cos(headingRad)
    );
    
    // Calculate new longitude
    const lon2 = lon1 + Math.atan2(
        Math.sin(headingRad) * Math.sin(distance / R) * Math.cos(lat1),
        Math.cos(distance / R) - Math.sin(lat1) * Math.sin(lat2)
    );
    
    // Convert back to degrees
    const newLat = (lat2 * 180) / Math.PI;
    const newLng = (lon2 * 180) / Math.PI;
    
    return [newLat, newLng];
}

/**
 * Calculate heading between two points in degrees (0-360)
 * 
 * @param {Number} lat1 - Starting latitude
 * @param {Number} lon1 - Starting longitude
 * @param {Number} lat2 - Ending latitude
 * @param {Number} lon2 - Ending longitude
 * @returns {Number} - Heading in degrees
 */
function calculateHeading(lat1, lon1, lat2, lon2) {
    // Convert to radians
    const lat1Rad = (lat1 * Math.PI) / 180;
    const lon1Rad = (lon1 * Math.PI) / 180;
    const lat2Rad = (lat2 * Math.PI) / 180;
    const lon2Rad = (lon2 * Math.PI) / 180;
    
    // Calculate heading
    const y = Math.sin(lon2Rad - lon1Rad) * Math.cos(lat2Rad);
    const x = Math.cos(lat1Rad) * Math.sin(lat2Rad) -
              Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(lon2Rad - lon1Rad);
    
    let heading = Math.atan2(y, x) * 180 / Math.PI;
    
    // Normalize to 0-360
    heading = (heading + 360) % 360;
    
    return heading;
}

/**
 * Calculate marker opacity based on time since last update
 * 
 * @param {Number} timeSinceUpdate - Time in milliseconds since last real update
 * @returns {Number} - Opacity value between 0.3 and 1.0
 */
function calculateOpacity(timeSinceUpdate) {
    if (timeSinceUpdate < FADE_START_TIME) {
        return 1.0;
    }
    
    const fadeTime = timeSinceUpdate - FADE_START_TIME;
    const fadeRange = MAX_PREDICTION_TIME - FADE_START_TIME;
    
    // Calculate opacity (minimum 0.3)
    return Math.max(0.3, 1.0 - (fadeTime / fadeRange) * 0.7);
}

/**
 * Update marker opacity
 * 
 * @param {Object} marker - The Leaflet marker
 * @param {Number} opacity - Opacity value between 0 and 1
 */
function updateMarkerOpacity(marker, opacity) {
    if (!marker || !marker._icon) return;
    
    marker._icon.style.opacity = opacity;
    
    if (marker._shadow) {
        marker._shadow.style.opacity = opacity;
    }
}

/**
 * Extract vehicle ID from marker
 * 
 * @param {Object} marker - The Leaflet marker
 * @returns {String|Number} - Vehicle ID or null
 */
function getVehicleIdFromMarker(marker) {
    // This is a simple implementation - you might need to adapt this
    // based on how you store vehicle IDs in your markers
    for (const id in vehicleMarkers) {
        if (vehicleMarkers[id] === marker) {
            return id;
        }
    }
    
    return null;
}