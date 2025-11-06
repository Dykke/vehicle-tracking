-- Complete Schema for Drive Monitoring System
-- This SQL file contains the complete schema for the database,
-- including all tables and fields for the 55% scope.

-- Drop existing tables if they exist
DROP TABLE IF EXISTS passenger_events;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS driver_action_logs;
DROP TABLE IF EXISTS location_logs;
DROP TABLE IF EXISTS notification_settings;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS alembic_version;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL,  -- 'admin', 'operator', 'driver'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    profile_image_url VARCHAR(500),
    current_latitude FLOAT,
    current_longitude FLOAT,
    accuracy FLOAT,
    created_by_id INTEGER,
    company_name VARCHAR(200),
    contact_number VARCHAR(50),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Create vehicles table
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    occupancy_status VARCHAR(20) DEFAULT 'vacant',
    last_speed_kmh FLOAT,
    current_latitude FLOAT,
    current_longitude FLOAT,
    last_updated TIMESTAMP,
    accuracy FLOAT,
    route VARCHAR(255),
    route_info TEXT,  -- JSON data stored as TEXT for SQLite compatibility
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Create location_logs table
CREATE TABLE location_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    accuracy FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Create notifications table
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data TEXT,  -- JSON data stored as TEXT for SQLite compatibility
    status VARCHAR(20) DEFAULT 'unread',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create notification_settings table
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT 1,
    notification_radius FLOAT DEFAULT 500.0,
    notify_specific_routes BOOLEAN DEFAULT 0,
    routes TEXT DEFAULT '[]',
    notification_cooldown INTEGER DEFAULT 300,
    last_notification_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create driver_action_logs table
CREATE TABLE driver_action_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    vehicle_id INTEGER,
    action VARCHAR(100) NOT NULL,
    meta_data TEXT,  -- JSON data stored as TEXT for SQLite compatibility
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES users(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

-- Create trips table
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    route_name VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (driver_id) REFERENCES users(id)
);

-- Create passenger_events table
CREATE TABLE passenger_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

-- Create alembic_version table for migrations
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
);

-- Insert a default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, user_type, is_active)
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:150000$KCncc4EZ$3b2970456cf8a0b1345278a8dd30753758d6d90375c7b06bd4a7cdca53a9b507', 'admin', 1);

-- Insert a default operator user (password: operator123)
INSERT INTO users (username, email, password_hash, user_type, is_active)
VALUES ('operator', 'operator@example.com', 'pbkdf2:sha256:150000$KCncc4EZ$3b2970456cf8a0b1345278a8dd30753758d6d90375c7b06bd4a7cdca53a9b507', 'operator', 1);