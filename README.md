# Drive Monitoring System

A real-time vehicle tracking system with user roles, interactive maps, and occupancy status monitoring.

## Features

- Real-time vehicle tracking on interactive maps
- User roles: Admin, Operator, Driver, and Public access
- Vehicle occupancy status (vacant/full)
- Driver action logging
- Trip management and passenger counting
- ETA calculation for vehicles
- Profile picture management
- Secure login system with rate limiting
- Responsive design for mobile and desktop

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite (local), PostgreSQL (production)
- **Real-time Communication**: Socket.IO
- **Maps**: Leaflet with OpenStreetMap

## Setup Instructions

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Reset the database (creates tables and default users):
   ```
   py reset_database.py
   ```
6. Start the server:
   ```
   py run_migration_and_server.py
   ```
7. Access the application at `http://localhost:5000`

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and customize as needed:

```
# Database Configuration
DATABASE_URL=sqlite:///app.db

# Admin Credentials (change these in production)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123


# Flask Secret Key (generate a secure random key for production)
SECRET_KEY=change_this_to_a_secure_random_key

# Security Settings
RATE_LIMIT_MAX_ATTEMPTS=5
RATE_LIMIT_LOCKOUT_TIME=300
PASSWORD_MIN_LENGTH=8
```

## Default Credentials

- **Admin**: username: `admin`, password: `admin123`

## Access URLs

- Public Map: `/` or `/public/map`
- Admin/Operator Login: `/login`

## Usage

### Public Users

- View the real-time map showing all active vehicles
- Click on vehicles to see their status (vacant/full)
- Calculate ETA for vehicles

### Operators

- Create and manage driver accounts
- Monitor vehicle locations and statuses
- View driver action logs
- Manage profile pictures for drivers

### Drivers

- Update vehicle occupancy status
- Log passenger boarding/alighting events
- Manage trips
- Change password

### Admin

- All operator capabilities
- Activate/deactivate driver accounts
- View system-wide logs and analytics

## Security Features

- Password hashing using pbkdf2:sha256
- Rate limiting for login attempts
- Input validation and sanitization
- Secure credential storage
- Protection against timing attacks
- Configurable security settings

## Deployment

For production deployment:

1. Set up a PostgreSQL database
2. Configure environment variables
3. Use a production WSGI server like Gunicorn
4. Set up HTTPS for secure communication

## License

This project is licensed under the MIT License - see the LICENSE file for details.