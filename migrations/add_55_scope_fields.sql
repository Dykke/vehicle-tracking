-- Migration script for 55% scope plan
-- Add new fields to existing tables and create new tables

-- Add new fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image_url VARCHAR(500);

-- Add new fields to vehicles table
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS occupancy_status VARCHAR(20) DEFAULT 'vacant';
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS last_speed_kmh FLOAT;

-- Create driver_action_logs table
CREATE TABLE IF NOT EXISTS driver_action_logs (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES users(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    action VARCHAR(100) NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trips table
CREATE TABLE IF NOT EXISTS trips (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
    driver_id INTEGER NOT NULL REFERENCES users(id),
    route_name VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create passenger_events table
CREATE TABLE IF NOT EXISTS passenger_events (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES trips(id),
    event_type VARCHAR(20) NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_driver_action_logs_driver_id ON driver_action_logs(driver_id);
CREATE INDEX IF NOT EXISTS idx_driver_action_logs_vehicle_id ON driver_action_logs(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_driver_action_logs_created_at ON driver_action_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_trips_vehicle_id ON trips(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trips_driver_id ON trips(driver_id);
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at);

CREATE INDEX IF NOT EXISTS idx_passenger_events_trip_id ON passenger_events(trip_id);
CREATE INDEX IF NOT EXISTS idx_passenger_events_created_at ON passenger_events(created_at);

-- Add constraints
ALTER TABLE driver_action_logs ADD CONSTRAINT IF NOT EXISTS chk_action_type 
    CHECK (action IN ('occupancy_change', 'trip_start', 'trip_end', 'passenger_event', 'password_change', 'driver_activated', 'driver_deactivated'));

ALTER TABLE passenger_events ADD CONSTRAINT IF NOT EXISTS chk_event_type 
    CHECK (event_type IN ('board', 'alight'));

ALTER TABLE trips ADD CONSTRAINT IF NOT EXISTS chk_trip_status 
    CHECK (status IN ('active', 'completed', 'cancelled'));

-- Update existing data to set default values
UPDATE users SET is_active = TRUE WHERE is_active IS NULL;
UPDATE vehicles SET occupancy_status = 'vacant' WHERE occupancy_status IS NULL;

-- Add comments for documentation
COMMENT ON TABLE driver_action_logs IS 'Logs all driver actions for audit trail';
COMMENT ON TABLE trips IS 'Tracks vehicle trips from start to end';
COMMENT ON TABLE passenger_events IS 'Records passenger boarding and alighting events';
COMMENT ON COLUMN users.is_active IS 'Whether the user account is active';
COMMENT ON COLUMN users.profile_image_url IS 'URL to user profile image';
COMMENT ON COLUMN vehicles.occupancy_status IS 'Current occupancy status: vacant or full';
COMMENT ON COLUMN vehicles.last_speed_kmh IS 'Last calculated speed in km/h';
