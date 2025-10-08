# Smart Car Trip Tracker 🚗📱🌐

A personal car trip diary that works on web + iOS app, tracks trips with GPS, auto-stops at geofences, and syncs securely (LAN or cloud).

## Features

### Phase 1 - Foundation ✅
- ✅ FastAPI backend with SQLite database
- ✅ JWT Authentication
- ✅ Core REST endpoints for trip management
- ✅ Geofence support with auto-stop functionality
- ✅ User settings management
- ✅ Docker containerization

### API Endpoints

#### Authentication
- `POST /register` - Register new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user info

#### Trip Management
- `POST /trip/start` - Start a new trip
- `POST /trip/update` - Update trip with location data
- `POST /trip/stop` - Stop current trip
- `GET /trips` - Get trip history
- `GET /trip/active` - Get current active trip
- `GET /trip/{trip_id}` - Get specific trip

#### Geofences
- `POST /geofences` - Create geofence
- `GET /geofences` - Get user's geofences

#### Settings
- `GET /settings` - Get user settings
- `PUT /settings` - Update user settings

## Quick Start

### Using Docker (Recommended)
```bash
# Clone and navigate to project
cd tracker

# Copy environment file
cp .env.example .env

# Build and run with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

## Database Schema

### Users
- id, username, email, hashed_password
- is_active, created_at
- Relationships: trips, geofences, settings

### Trips
- id, user_id, title, description
- start_time, end_time, start/end coordinates
- total_distance, is_active, created_at
- Relationships: user, trip_points

### TripPoints
- id, trip_id, latitude, longitude
- altitude, speed, accuracy, timestamp
- Relationship: trip

### Geofences
- id, user_id, name, description
- latitude, longitude, radius, action
- is_active, created_at
- Relationship: user

### UserSettings
- id, user_id, auto_start_trips
- auto_stop_at_geofences, location_update_interval
- distance_threshold, enable_notifications, sync_method
- Relationship: user

## API Usage Examples

### 1. Register and Login
```bash
# Register
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'

# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret123"

# Response: {"access_token": "...", "token_type": "bearer"}
```

### 2. Start a Trip
```bash
curl -X POST "http://localhost:8000/trip/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "title": "Drive to work",
    "description": "Morning commute"
  }'
```

### 3. Update Trip Location
```bash
curl -X POST "http://localhost:8000/trip/update" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7849,
    "longitude": -122.4094,
    "speed": 45.5,
    "accuracy": 5.0
  }'
```

### 4. Stop Trip
```bash
curl -X POST "http://localhost:8000/trip/stop" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7949,
    "longitude": -122.3994
  }'
```

### 5. Create Geofence
```bash
curl -X POST "http://localhost:8000/geofences" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home",
    "description": "Auto-stop when arriving home",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "radius": 100,
    "action": "stop"
  }'
```

## Features

### Smart Geofencing
- Automatic trip stopping when entering designated areas
- Multiple geofence actions: stop, start, notify
- Configurable radius and user-specific geofences

### Location Tracking
- Continuous GPS tracking during trips
- Speed, altitude, and accuracy recording
- Distance calculation using Haversine formula

### User Settings
- Configurable auto-start/stop behavior
- Location update intervals
- Sync preferences (cloud, LAN, manual)

## Development

### Project Structure
```
tracker/
├── main.py           # FastAPI application and routes
├── database.py       # SQLAlchemy models and database config
├── schemas.py        # Pydantic models for API
├── crud.py          # Database operations
├── auth.py          # Authentication utilities
├── requirements.txt  # Python dependencies
├── Dockerfile       # Docker container config
├── docker-compose.yml # Docker Compose setup
└── .env.example     # Environment variables template
```

### Next Steps (Phase 2)
- [ ] Real-time WebSocket connections
- [ ] Mobile app (React Native or Flutter)
- [ ] Advanced analytics and reporting
- [ ] Export functionality (GPX, KML)
- [ ] Social features and trip sharing
- [ ] Offline mode support

## License

MIT License - see LICENSE file for details.