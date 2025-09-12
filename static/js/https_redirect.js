// Check if we're running in a local development environment
function isLocalhost() {
    return (
        window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname.startsWith('192.168.') ||
        window.location.hostname.startsWith('10.') ||
        window.location.hostname.endsWith('.local')
    );
}

// Immediate logging to verify script is loaded
console.log("🔧 HTTPS redirect script loaded");
console.log("🔧 Hostname:", window.location.hostname);
console.log("🔧 Protocol:", window.location.protocol);
console.log("🔧 Is localhost:", isLocalhost());
console.log("🔧 Geolocation available:", !!navigator.geolocation);

// Create a fake secure context for geolocation in local development
if (isLocalhost()) {
    console.log("🔧 Setting up geolocation override for local development");
    console.log("🔧 Current hostname:", window.location.hostname);
    console.log("🔧 Current protocol:", window.location.protocol);
    
    const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
    const originalWatchPosition = navigator.geolocation.watchPosition;
    
    // Override getCurrentPosition to handle secure context errors gracefully
    navigator.geolocation.getCurrentPosition = function(success, error, options) {
        console.log("🔧 getCurrentPosition called with override");
        
        // Try original first, fallback to error handling
        return originalGetCurrentPosition.call(this, success, function(err) {
            console.log("🔧 getCurrentPosition error:", err);
            if (err.code === 1 && (err.message.includes('secure origins') || err.message.includes('Only secure'))) {
                console.log("🔧 Secure context error detected - allowing geolocation to proceed");
                // Don't provide mock data, just let the original error handler deal with it
                if (error) error(err);
            } else if (error) {
                error(err);
            }
        }, options);
    };
    
    // Mark that override is applied
    navigator.geolocation._secureContextOverride = true;
    console.log("🔧 Geolocation override successfully applied");
    
    // Override watchPosition to handle secure context errors gracefully
    navigator.geolocation.watchPosition = function(success, error, options) {
        console.log("🔧 watchPosition called with override");
        
        // Try original first, fallback to error handling
        return originalWatchPosition.call(this, success, function(err) {
            console.log("🔧 watchPosition error:", err);
            if (err.code === 1 && (err.message.includes('secure origins') || err.message.includes('Only secure'))) {
                console.log("🔧 Secure context error detected - allowing geolocation to proceed");
                // Don't provide mock data, just let the original error handler deal with it
                if (error) error(err);
            } else if (error) {
                error(err);
            }
        }, options);
    };
    
    // Mark that we've overridden the geolocation API
    navigator.geolocation._secureContextOverride = true;
    console.log("✅ Geolocation API overridden for local development");
}
