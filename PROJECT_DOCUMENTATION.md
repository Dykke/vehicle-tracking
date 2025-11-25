# Drive Monitoring System - Technical Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Frontend Architecture](#frontend-architecture)
5. [Backend Architecture](#backend-architecture)
6. [Data Flow and System Flow](#data-flow-and-system-flow)
7. [User Roles and Permissions](#user-roles-and-permissions)
8. [Key Features](#key-features)
9. [API Endpoints](#api-endpoints)
10. [Real-time Communication](#real-time-communication)
11. [Database Schema](#database-schema)
12. [Security Features](#security-features)
13. [Deployment](#deployment)

---

## Project Overview

The Drive Monitoring System is a comprehensive real-time vehicle tracking and management platform designed for transportation companies. The system enables real-time monitoring of vehicle locations, occupancy status, driver management, and provides a public-facing map interface for commuters to track available vehicles.

### Core Purpose

- **Real-time Vehicle Tracking**: Monitor vehicle locations and movements in real-time
- **Occupancy Management**: Track vehicle capacity and availability status
- **Driver Management**: Manage driver accounts, assignments, and actions
- **Public Access**: Provide commuters with real-time vehicle information
- **Route Management**: Track and manage vehicle routes
- **Action Logging**: Comprehensive logging of all system activities

---

## System Architecture

The system follows a **client-server architecture** with a **Flask-based backend** and a **JavaScript-based frontend**. Real-time communication is handled through **WebSocket connections** using Socket.IO.

### High-Level Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (Frontend)     │
└────────┬────────┘
         │
         │ HTTP/HTTPS
         │ WebSocket (Socket.IO)
         │
┌────────▼────────┐
│  Flask Server   │
│   (Backend)     │
└────────┬────────┘
         │
         │ SQLAlchemy ORM
         │
┌────────▼────────┐
│   Database      │
│ (SQLite/PostgreSQL)│
└─────────────────┘
```

### Component Overview

1. **Frontend Layer**: HTML templates, CSS styling, and JavaScript for user interaction
2. **Backend Layer**: Flask application with route handlers and business logic
3. **Real-time Layer**: Socket.IO for bidirectional communication
4. **Data Layer**: SQLAlchemy ORM with SQLite (development) or PostgreSQL (production)
5. **Authentication Layer**: Flask-Login for session management

---

## Technology Stack

### Frontend Technologies

- **HTML5**: Structure and semantic markup
- **CSS3**: Styling and responsive design
- **JavaScript (ES6+)**: Client-side logic and interactivity
- **Leaflet.js**: Interactive map rendering and visualization
- **OpenStreetMap**: Map tiles and geocoding services
- **Socket.IO Client**: Real-time WebSocket communication

### Backend Technologies

- **Python 3.x**: Programming language
- **Flask 2.0.1**: Web framework
- **Flask-Login 0.5.0**: User session management
- **Flask-SocketIO 5.1.1**: WebSocket support for real-time features
- **SQLAlchemy 1.4.1**: Database ORM
- **Flask-CORS 5.0.0**: Cross-origin resource sharing
- **Flask-Migrate 4.1.0**: Database migrations
- **Werkzeug 2.0.1**: WSGI utilities and password hashing

### Database

- **SQLite**: Development and local deployment
- **PostgreSQL**: Production deployment (via pg8000 driver)

### Additional Libraries

- **Geopy 2.4.0**: Geocoding and distance calculations
- **APScheduler 3.11.0**: Task scheduling
- **python-dotenv 0.19.0**: Environment variable management
- **Gunicorn 21.2.0**: Production WSGI server

---

## Frontend Architecture

### Structure

The frontend is organized into several key components:

```
templates/
├── base.html              # Base template with common layout
├── index.html             # Public landing page
├── auth/
│   ├── login.html         # Login page
│   └── register.html      # Registration page
├── public/
│   └── map.html           # Public vehicle map
├── operator/
│   ├── dashboard.html     # Operator control panel
│   ├── manage_drivers.html
│   ├── manage_vehicle.html
│   └── vehicle_controls.html
├── driver/
│   ├── dashboard.html     # Driver interface
│   └── settings.html
└── commuter/
    └── dashboard.html     # Commuter interface
```

### JavaScript Modules

```
static/js/
├── socket_manager.js      # Socket.IO connection management
├── driver-dashboard.js    # Driver dashboard logic
├── driver-occupancy.js    # Occupancy management
├── driver_actions.js      # Driver action handlers
├── smooth_tracking.js     # Smooth vehicle tracking
└── https_redirect.js      # HTTPS redirection
```

### Frontend Flow

1. **Page Load**: User accesses a route (e.g., `/`, `/operator/dashboard`)
2. **Template Rendering**: Flask renders the appropriate HTML template
3. **JavaScript Initialization**: Client-side JavaScript initializes:
   - Map rendering (Leaflet)
   - Socket.IO connection
   - Event listeners
   - UI components
4. **Data Fetching**: Initial data loaded via REST API calls
5. **Real-time Updates**: Socket.IO receives real-time updates
6. **User Interactions**: User actions trigger API calls or Socket.IO events

### Key Frontend Features

#### Map Integration (Leaflet)

- **Interactive Maps**: Display vehicles as markers on OpenStreetMap
- **Real-time Updates**: Vehicle markers update position in real-time
- **Route Filtering**: Filter vehicles by route
- **ETA Calculation**: Calculate estimated time of arrival
- **Marker Clustering**: Group nearby vehicles for better visualization

#### Real-time Communication

- **Socket.IO Connection**: Maintains persistent WebSocket connection
- **Automatic Reconnection**: Handles connection drops gracefully
- **Room-based Updates**: Users receive updates for relevant vehicles only
- **Connection Status**: Visual indicator of connection status

---

## Backend Architecture

### Structure

The backend follows a **modular blueprint architecture**:

```
app.py                    # Main application entry point
routes/
├── auth.py              # Authentication routes
├── admin.py             # Admin-specific routes
├── operator.py          # Operator routes
├── driver.py            # Driver routes
├── commuter.py          # Commuter routes
├── public.py            # Public routes
├── api.py               # REST API endpoints
└── notifications.py     # Notification handling

models/
├── user.py              # User model and related models
├── vehicle.py           # Vehicle model
├── location_log.py      # Location tracking model
└── notification.py      # Notification models

events_optimized.py      # Socket.IO event handlers
db_config.py             # Database configuration
secure_config.py         # Security configuration
```

### Backend Flow

1. **Request Reception**: Flask receives HTTP request or WebSocket event
2. **Route Matching**: Flask matches URL to appropriate blueprint route
3. **Authentication Check**: Flask-Login verifies user authentication (if required)
4. **Permission Validation**: Checks user role and permissions
5. **Business Logic**: Executes route handler logic
6. **Database Operations**: Performs CRUD operations via SQLAlchemy
7. **Response Generation**: Returns JSON response or renders template
8. **Real-time Broadcasting**: Emits Socket.IO events to connected clients (if applicable)

### Key Backend Components

#### Application Initialization (`app.py`)

- **Flask App Creation**: Initializes Flask application
- **Database Setup**: Configures SQLAlchemy connection
- **Blueprint Registration**: Registers all route blueprints
- **Socket.IO Initialization**: Sets up WebSocket server
- **Session Configuration**: Configures Flask session settings
- **Logging Setup**: Configures application logging

#### Route Handlers

Each blueprint handles specific functionality:

- **auth.py**: Login, logout, registration
- **admin.py**: Admin dashboard, user management, system logs
- **operator.py**: Vehicle management, driver management, monitoring
- **driver.py**: Driver dashboard, occupancy updates, trip management
- **commuter.py**: Commuter dashboard, vehicle search
- **public.py**: Public map, vehicle listing
- **api.py**: RESTful API endpoints for AJAX calls

#### Event Handlers (`events_optimized.py`)

Handles all Socket.IO events:

- **Connection Management**: Client connect/disconnect
- **Location Updates**: Vehicle location updates from drivers
- **Vehicle Position Requests**: Broadcast vehicle positions
- **Room Management**: Join/leave vehicle-specific rooms
- **Status Updates**: Vehicle status changes

---

## Data Flow and System Flow

### User Authentication Flow

```
1. User accesses /login
2. Frontend renders login.html
3. User submits credentials
4. POST request to /login
5. Backend validates credentials:
   - Checks rate limiting
   - Verifies username/password
   - Checks user type and active status
6. Flask-Login creates session
7. Redirect based on user type:
   - Admin → /admin/dashboard
   - Operator → /operator/dashboard
   - Driver → /driver/dashboard
   - Commuter → /commuter/dashboard
```

### Vehicle Location Update Flow

```
1. Driver's device sends location update
2. Frontend JavaScript captures GPS coordinates
3. Socket.IO emits 'location_update' event with:
   - vehicle_id
   - latitude
   - longitude
   - accuracy
4. Backend receives event in events_optimized.py
5. Backend validates:
   - User authentication
   - Vehicle ownership/assignment
   - Data validity
6. Backend updates database:
   - Updates Vehicle.current_latitude
   - Updates Vehicle.current_longitude
   - Updates Vehicle.last_updated
   - Creates LocationLog entry
   - Calculates speed (if previous location exists)
7. Backend broadcasts update:
   - Emits 'vehicle_update' to all clients
   - Emits to vehicle-specific room
8. All connected clients receive update
9. Frontend updates map markers
```

### Public Map View Flow

```
1. User accesses / (public route)
2. Frontend renders public/map.html
3. JavaScript initializes:
   - Leaflet map
   - Socket.IO connection
4. Initial data load:
   - GET /public/vehicles/active
   - Backend queries active vehicles
   - Returns JSON with vehicle data
5. Frontend displays vehicles as map markers
6. Socket.IO connection established
7. Client emits 'request_vehicle_positions'
8. Backend responds with current vehicle positions
9. Real-time updates:
   - Backend broadcasts 'vehicle_positions' on updates
   - Frontend updates markers in real-time
```

### Occupancy Status Update Flow

```
1. Driver clicks occupancy button (vacant/full)
2. Frontend JavaScript sends POST request:
   - POST /driver/vehicle/{id}/occupancy
   - Body: {status: 'vacant' or 'full'}
3. Backend validates:
   - User is authenticated driver
   - Vehicle is assigned to driver
4. Backend updates:
   - Vehicle.occupancy_status
   - Creates DriverActionLog entry
5. Backend broadcasts:
   - Emits 'vehicle_update' via Socket.IO
6. Frontend receives update and refreshes UI
7. Public map updates vehicle marker color
```

### Route Management Flow

```
1. Operator/Driver sets route:
   - POST /api/vehicles/{id}/route
   - Body: {route: "A to B"}
2. Backend processes:
   - Parses route format
   - Creates route_info JSON
   - Updates Vehicle.route and Vehicle.route_info
   - Logs action
3. Backend broadcasts route update
4. Frontend displays route information
5. Public map filters by route (if applicable)
```

---

## User Roles and Permissions

### Admin

**Capabilities:**
- Full system access
- Create and manage operators
- Activate/deactivate any user account
- View all vehicles and drivers
- Access system-wide logs
- Manage all vehicles
- View all action logs

**Routes:**
- `/admin/dashboard` - Admin control panel
- `/admin/action_logs` - System logs

### Operator

**Capabilities:**
- Create and manage driver accounts
- Manage vehicles owned by operator
- Monitor vehicle locations and statuses
- View driver action logs
- Manage driver profile pictures
- Assign drivers to vehicles
- Set vehicle routes
- View operator-specific action logs

**Routes:**
- `/operator/dashboard` - Operator dashboard
- `/operator/manage_drivers` - Driver management
- `/operator/manage_vehicle` - Vehicle management
- `/operator/vehicle_controls` - Vehicle controls
- `/operator/action_logs` - Operator logs

### Driver

**Capabilities:**
- Update assigned vehicle location
- Change occupancy status (vacant/full)
- Log passenger boarding/alighting events
- Manage trips
- Start/abort routes
- Change password
- View own action logs

**Routes:**
- `/driver/dashboard` - Driver dashboard
- `/driver/settings` - Driver settings
- `/driver/change_password` - Password change

### Commuter

**Capabilities:**
- View real-time vehicle map
- Search for vehicles
- Calculate ETA to vehicles
- Filter vehicles by route
- View vehicle occupancy status
- Track user location

**Routes:**
- `/commuter/dashboard` - Commuter dashboard

### Public (Unauthenticated)

**Capabilities:**
- View public vehicle map
- See active vehicles
- Click vehicles for basic information
- Calculate ETA

**Routes:**
- `/` or `/public/map` - Public map

---

## Key Features

### 1. Real-time Vehicle Tracking

- **GPS Integration**: Vehicles send location updates via GPS
- **Live Updates**: All clients see location updates in real-time
- **Speed Calculation**: System calculates vehicle speed from location changes
- **Location History**: Stores location logs for historical tracking
- **Accuracy Tracking**: Tracks GPS accuracy for each update

### 2. Occupancy Management

- **Status Indicators**: Visual indicators for vacant/full status
- **Driver Updates**: Drivers can update occupancy in real-time
- **Public Visibility**: Commuters see occupancy status on map
- **Action Logging**: All occupancy changes are logged

### 3. Route Management

- **Route Assignment**: Operators can assign routes to vehicles
- **Route Format**: Supports "Origin to Destination" format
- **Route Information**: Stores structured route data
- **Route Filtering**: Public map can filter by route
- **Route Abort**: Drivers can abort routes

### 4. Driver Management

- **Account Creation**: Operators create driver accounts
- **Vehicle Assignment**: Assign vehicles to drivers
- **Profile Pictures**: Upload and manage driver photos
- **Action Logging**: Track all driver actions
- **Account Activation**: Activate/deactivate driver accounts

### 5. Trip Management

- **Trip Creation**: Drivers can start trips
- **Passenger Events**: Log passenger boarding/alighting
- **Trip Status**: Track active, completed, or cancelled trips
- **Trip History**: View past trips

### 6. Notification System

- **Real-time Notifications**: Socket.IO-based notifications
- **Notification Settings**: User-configurable notification preferences
- **Vehicle Approaching**: Alerts for nearby vehicles
- **System Notifications**: Important system updates

### 7. Action Logging

- **Driver Actions**: Log all driver activities
- **Operator Actions**: Log operator management actions
- **Audit Trail**: Complete audit trail for compliance
- **Action History**: View historical actions

### 8. Map Features

- **Interactive Maps**: Leaflet-based interactive maps
- **Marker Clustering**: Groups nearby vehicles
- **Route Display**: Shows vehicle routes
- **ETA Calculation**: Calculates estimated arrival time
- **User Location**: Tracks and displays user location
- **Map Controls**: Zoom, pan, center controls

---

## API Endpoints

### Authentication Endpoints

- `GET /login` - Display login page
- `POST /login` - Process login
- `GET /logout` - Logout user
- `GET /register` - Display registration page
- `POST /register` - Process registration

### Public Endpoints

- `GET /` - Public map page
- `GET /public/map` - Public map page
- `GET /public/vehicles/active` - Get active vehicles (public)

### API Endpoints (REST)

- `GET /api/vehicles/active` - Get all active vehicles
- `GET /api/vehicles/<id>` - Get vehicle by ID (authenticated)
- `GET /api/vehicles/operator` - Get operator's vehicles
- `POST /api/vehicles/<id>/route` - Update vehicle route
- `DELETE /api/vehicles/<id>/route` - Abort vehicle route
- `GET /api/geocode/search` - Geocode search (proxy)
- `GET /api/geocode/reverse` - Reverse geocoding (proxy)

### Operator Endpoints

- `GET /operator/dashboard` - Operator dashboard
- `GET /operator/manage_drivers` - Driver management
- `GET /operator/manage_vehicle` - Vehicle management
- `POST /operator/vehicle/<id>/update` - Update vehicle location
- `GET /operator/action_logs` - Operator action logs

### Driver Endpoints

- `GET /driver/dashboard` - Driver dashboard
- `POST /driver/vehicle/<id>/occupancy` - Update occupancy
- `GET /driver/settings` - Driver settings
- `GET /driver/action_logs` - Driver action logs

### Commuter Endpoints

- `GET /commuter/dashboard` - Commuter dashboard

### Admin Endpoints

- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/action_logs` - System action logs

### Health Check Endpoints

- `GET /ping` - Simple ping endpoint
- `GET /health` - Health check (no database)
- `GET /db-ping` - Database connectivity check

---

## Real-time Communication

### Socket.IO Events

#### Client to Server Events

- `connect` - Client connects to server
- `disconnect` - Client disconnects
- `location_update` - Send vehicle location update
  - Data: `{vehicle_id, latitude, longitude, accuracy}`
- `request_vehicle_positions` - Request current vehicle positions
- `join_vehicle_room` - Join vehicle-specific room
  - Data: `{vehicle_id}`
- `driver_vehicle_update` - Driver updates vehicle info
- `driver_status_update` - Driver updates status

#### Server to Client Events

- `connect_ack` - Connection acknowledgement
  - Data: `{status: 'connected', timestamp}`
- `vehicle_positions` - Broadcast vehicle positions
  - Data: `{vehicles: [...]}`
- `vehicle_update` - Individual vehicle update
  - Data: `{vehicle_id, ...vehicle_data}`
- `notification` - User notification
- `vehicle_approaching` - Vehicle approaching alert

### Room Management

The system uses Socket.IO rooms for efficient message broadcasting:

- **Global Room**: `all_clients` - All connected clients
- **User Room**: `user_{user_id}` - User-specific room
- **Vehicle Room**: `vehicle_{vehicle_id}` - Vehicle-specific room

### Connection Handling

- **Automatic Reconnection**: Clients automatically reconnect on disconnect
- **Connection Status**: Visual indicator of connection status
- **Reconnection Delay**: Exponential backoff for reconnection attempts
- **Heartbeat**: Connection keep-alive mechanism

---

## Database Schema

### Users Table

```sql
users
├── id (Primary Key)
├── username (Unique)
├── email (Unique)
├── password_hash
├── user_type (admin, operator, driver, commuter)
├── first_name
├── middle_name
├── last_name
├── is_active
├── profile_image_url
├── current_latitude
├── current_longitude
├── accuracy
├── company_name
├── contact_number
├── created_by_id (Foreign Key → users.id)
└── created_at
```

### Vehicles Table

```sql
vehicles
├── id (Primary Key)
├── registration_number (Unique)
├── vehicle_type
├── capacity
├── status (active, inactive, delayed)
├── occupancy_status (empty, vacant, full)
├── current_latitude
├── current_longitude
├── last_speed_kmh
├── accuracy
├── route
├── route_info (JSON)
├── owner_id (Foreign Key → users.id)
├── assigned_driver_id (Foreign Key → users.id)
├── last_updated
└── created_at
```

### Location Logs Table

```sql
location_logs
├── id (Primary Key)
├── vehicle_id (Foreign Key → vehicles.id)
├── latitude
├── longitude
├── speed_kmh
├── accuracy
├── heading
├── altitude
├── route_info
└── timestamp
```

### Trips Table

```sql
trips
├── id (Primary Key)
├── vehicle_id (Foreign Key → vehicles.id)
├── driver_id (Foreign Key → users.id)
├── route_name
├── start_time
├── end_time
├── status (active, completed, cancelled)
└── created_at
```

### Passenger Events Table

```sql
passenger_events
├── id (Primary Key)
├── trip_id (Foreign Key → trips.id)
├── event_type (board, alight)
├── count
├── notes
└── created_at
```

### Driver Action Logs Table

```sql
driver_action_logs
├── id (Primary Key)
├── driver_id (Foreign Key → users.id)
├── vehicle_id (Foreign Key → vehicles.id)
├── action (occupancy_change, route_start, route_abort, etc.)
├── meta_data (JSON)
└── created_at
```

### Operator Action Logs Table

```sql
operator_action_logs
├── id (Primary Key)
├── operator_id (Foreign Key → users.id)
├── action (driver_created, vehicle_added, etc.)
├── target_type (driver, vehicle, system)
├── target_id
├── meta_data (JSON)
└── created_at
```

### Notifications Table

```sql
notifications
├── id (Primary Key)
├── user_id (Foreign Key → users.id)
├── title
├── message
├── type
├── is_read
└── created_at
```

### Notification Settings Table

```sql
notification_settings
├── id (Primary Key)
├── user_id (Foreign Key → users.id)
├── vehicle_approaching (Boolean)
├── occupancy_change (Boolean)
└── route_update (Boolean)
```

---

## Security Features

### Authentication Security

- **Password Hashing**: Uses pbkdf2:sha256 with salt
- **Session Management**: Flask-Login for secure session handling
- **Rate Limiting**: Prevents brute force attacks
  - Max attempts: 5
  - Lockout time: 300 seconds
- **Secure Comparison**: Constant-time string comparison to prevent timing attacks
- **Input Validation**: Validates username and email formats
- **Password Requirements**: Minimum length enforcement

### Authorization

- **Role-Based Access Control**: User types determine access levels
- **Resource Ownership**: Operators can only manage their own vehicles
- **Driver Assignment**: Drivers can only update assigned vehicles
- **Route Protection**: Protected routes require authentication

### Data Security

- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping prevents cross-site scripting
- **CSRF Protection**: Session-based CSRF protection
- **Secure Headers**: CORS configuration for cross-origin requests

### Session Security

- **Session Lifetime**: 24-hour session lifetime
- **Session Refresh**: Sessions refresh on each request
- **Secure Cookies**: HTTPOnly and SameSite cookie settings
- **Session Cookie Name**: Custom cookie name for identification

---

## Deployment

### Development Setup

1. **Environment Setup**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Database Initialization**:
   ```bash
   python reset_database.py
   ```

3. **Run Server**:
   ```bash
   python run_migration_and_server.py
   ```

4. **Access Application**:
   - URL: `http://localhost:5000`
   - Default Admin: `admin` / `admin123`

### Production Deployment

1. **Database**: Use PostgreSQL instead of SQLite
2. **WSGI Server**: Use Gunicorn for production
3. **Environment Variables**: Configure via `.env` file:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SECRET_KEY`: Secure random key
   - `ADMIN_USERNAME`: Admin username
   - `ADMIN_PASSWORD`: Secure admin password
   - `FLASK_ENV`: Set to `production`

4. **HTTPS**: Enable HTTPS for secure communication
5. **Static Files**: Serve static files via web server (Nginx)
6. **Process Management**: Use systemd or supervisor

### Environment Configuration

Required environment variables:

```
DATABASE_URL=postgresql://user:pass@host/dbname
SECRET_KEY=your-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000
RATE_LIMIT_MAX_ATTEMPTS=5
RATE_LIMIT_LOCKOUT_TIME=300
PASSWORD_MIN_LENGTH=8
```

### Deployment Platforms

- **Render**: Configured via `render.yaml`
- **Heroku**: Use `Procfile` and `runtime.txt`
- **VPS**: Manual deployment with Gunicorn + Nginx
- **Docker**: Can be containerized (Dockerfile not included)

---

## System Flow Summary

### Complete User Journey Example

**Scenario: Driver Updates Vehicle Location**

1. **Driver logs in** → Authentication flow
2. **Driver accesses dashboard** → `/driver/dashboard`
3. **JavaScript initializes**:
   - Map loads
   - Socket.IO connects
   - GPS tracking starts
4. **Location update triggered**:
   - GPS provides coordinates
   - JavaScript captures location
   - Socket.IO emits `location_update`
5. **Backend processes**:
   - Validates driver and vehicle
   - Updates database
   - Creates location log
   - Calculates speed
6. **Backend broadcasts**:
   - Emits `vehicle_update` to all clients
   - Updates vehicle room
7. **All clients receive update**:
   - Public map updates marker
   - Operator dashboard refreshes
   - Commuter dashboard updates
8. **Real-time visualization**:
   - Map markers move
   - Status indicators update
   - ETA recalculates

### Data Synchronization

- **Real-time**: Socket.IO for immediate updates
- **Polling Fallback**: REST API for initial loads
- **Caching**: Vehicle positions cached for 5 seconds
- **Database**: Single source of truth
- **Conflict Resolution**: Last update wins

---

## Conclusion

The Drive Monitoring System is a comprehensive solution for real-time vehicle tracking and management. It combines modern web technologies with robust backend architecture to provide a scalable, secure, and user-friendly platform for transportation management.

The system's modular design allows for easy extension and maintenance, while the real-time communication layer ensures all users have access to up-to-date information. The role-based access control ensures security while providing appropriate functionality to each user type.

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Prepared For**: Client Documentation

