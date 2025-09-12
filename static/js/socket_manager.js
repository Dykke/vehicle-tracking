/**
 * Socket.IO Connection Manager
 * 
 * This module provides robust Socket.IO connection management with:
 * - Automatic reconnection
 * - Connection status tracking
 * - Event handling for connection state changes
 */

// Configuration
const RECONNECTION_DELAY = 1000;        // Initial delay before reconnection attempt (ms)
const RECONNECTION_DELAY_MAX = 5000;    // Maximum delay between reconnection attempts (ms)
const RECONNECTION_ATTEMPTS = Infinity; // Number of reconnection attempts before giving up

// Socket instance
let socket = null;

// Connection status
let connectionStatus = 'disconnected';

// Event callbacks
const eventCallbacks = {
    'connect': [],
    'disconnect': [],
    'reconnect': [],
    'reconnect_attempt': [],
    'reconnect_error': [],
    'reconnect_failed': [],
    'vehicle_positions': [],
    'vehicle_update': []
};

/**
 * Initialize Socket.IO connection
 * 
 * @param {Object} options - Additional Socket.IO options
 * @returns {Object} - The Socket.IO instance
 */
function initSocketConnection(options = {}) {
    // Default options
    const defaultOptions = {
        reconnection: true,
        reconnectionDelay: RECONNECTION_DELAY,
        reconnectionDelayMax: RECONNECTION_DELAY_MAX,
        reconnectionAttempts: RECONNECTION_ATTEMPTS,
        timeout: 20000,
        autoConnect: true
    };
    
    // Merge default options with provided options
    const socketOptions = { ...defaultOptions, ...options };
    
    // Initialize Socket.IO
    socket = io(socketOptions);
    
    // Set up event listeners
    socket.on('connect', () => {
        console.log('Socket.IO connected');
        connectionStatus = 'connected';
        triggerCallbacks('connect');
    });
    
    socket.on('disconnect', (reason) => {
        console.log(`Socket.IO disconnected: ${reason}`);
        connectionStatus = 'disconnected';
        triggerCallbacks('disconnect', reason);
    });
    
    socket.on('reconnect', (attemptNumber) => {
        console.log(`Socket.IO reconnected after ${attemptNumber} attempts`);
        connectionStatus = 'connected';
        triggerCallbacks('reconnect', attemptNumber);
    });
    
    socket.on('reconnect_attempt', (attemptNumber) => {
        console.log(`Socket.IO reconnection attempt ${attemptNumber}`);
        connectionStatus = 'connecting';
        triggerCallbacks('reconnect_attempt', attemptNumber);
    });
    
    socket.on('reconnect_error', (error) => {
        console.error('Socket.IO reconnection error:', error);
        triggerCallbacks('reconnect_error', error);
    });
    
    socket.on('reconnect_failed', () => {
        console.error('Socket.IO reconnection failed');
        triggerCallbacks('reconnect_failed');
    });
    
    // Set up event listeners for vehicle data
    socket.on('vehicle_positions', (data) => {
        triggerCallbacks('vehicle_positions', data);
    });
    
    socket.on('vehicle_update', (data) => {
        triggerCallbacks('vehicle_update', data);
    });
    
    return socket;
}

/**
 * Get the current Socket.IO instance
 * 
 * @returns {Object|null} - The Socket.IO instance or null if not initialized
 */
function getSocket() {
    return socket;
}

/**
 * Get the current connection status
 * 
 * @returns {String} - 'connected', 'disconnected', or 'connecting'
 */
function getConnectionStatus() {
    return connectionStatus;
}

/**
 * Add an event listener
 * 
 * @param {String} event - The event name
 * @param {Function} callback - The callback function
 */
function addEventListener(event, callback) {
    if (!eventCallbacks[event]) {
        eventCallbacks[event] = [];
    }
    
    eventCallbacks[event].push(callback);
}

/**
 * Remove an event listener
 * 
 * @param {String} event - The event name
 * @param {Function} callback - The callback function to remove
 */
function removeEventListener(event, callback) {
    if (!eventCallbacks[event]) return;
    
    const index = eventCallbacks[event].indexOf(callback);
    if (index !== -1) {
        eventCallbacks[event].splice(index, 1);
    }
}

/**
 * Trigger callbacks for an event
 * 
 * @param {String} event - The event name
 * @param {...any} args - Arguments to pass to the callbacks
 */
function triggerCallbacks(event, ...args) {
    if (!eventCallbacks[event]) return;
    
    eventCallbacks[event].forEach(callback => {
        try {
            callback(...args);
        } catch (error) {
            console.error(`Error in ${event} callback:`, error);
        }
    });
}

/**
 * Manually connect to the Socket.IO server
 */
function connect() {
    if (socket && socket.disconnected) {
        socket.connect();
    }
}

/**
 * Manually disconnect from the Socket.IO server
 */
function disconnect() {
    if (socket && socket.connected) {
        socket.disconnect();
    }
}

/**
 * Emit an event to the server
 * 
 * @param {String} event - The event name
 * @param {any} data - The data to send
 * @param {Function} callback - Optional callback for acknowledgement
 */
function emit(event, data, callback) {
    if (!socket) {
        console.error('Socket.IO not initialized');
        return;
    }
    
    if (socket.connected) {
        socket.emit(event, data, callback);
    } else {
        console.warn('Socket.IO not connected, event not sent:', event);
    }
}

/**
 * Request vehicle positions from the server
 */
function requestVehiclePositions() {
    emit('request_vehicle_positions');
}

// Export functions
window.socketManager = {
    initSocketConnection,
    getSocket,
    getConnectionStatus,
    addEventListener,
    removeEventListener,
    connect,
    disconnect,
    emit,
    requestVehiclePositions
};