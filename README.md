# Smart Car Trip Tracker 🚗📱🌐

A personal car trip diary that works on web + iOS app, tracks trips with GPS, auto-stops at geofences, and syncs securely (LAN or cloud).

## 📁 Project Structure

```
tracker/
├── 📁 src/                      # Source code
│   ├── main.py                 # Main FastAPI application
│   ├── auth.py                 # Authentication utilities
│   ├── crud.py                 # Database CRUD operations
│   ├── database.py             # Database models & configuration
│   ├── schemas.py              # Pydantic schemas for API validation
│   └── main_old.py             # Backup of original main file
├── 📁 config/                  # Configuration files
│   ├── .env.example           # Environment variables template
│   ├── Dockerfile             # Docker container configuration
│   └── docker-compose.yml     # Docker Compose setup
├── 📁 data/                    # Data storage
│   └── trip_tracker.db        # SQLite database file
├── 📁 docs/                    # Documentation
│   └── README.md              # Additional documentation
├── 📁 scripts/                 # Utility scripts
│   ├── setup.sh               # Quick setup script
│   └── test_api.py             # API testing script
├── 📄 .gitignore              # Git ignore rules
├── 📄 README.md               # This file
├── 📄 requirements.txt        # Python dependencies
└── 📁 .venv/                  # Virtual environment
```

## 🚀 Quick Start

### Method 1: Using the Setup Script (Recommended)
```bash
# Run the automated setup script
./scripts/setup.sh

# Then start the server
cd src && python3 main.py
```

### Method 2: Manual Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp config/.env.example .env

# Start the server
cd src && python3 main.py
```

### Method 3: Using Uvicorn Directly
```bash
# Navigate to source directory and start with uvicorn
cd src && uvicorn main:app --host 127.0.0.1 --port 8001

# Or with reload (may cause file watch issues)
cd src && uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### Method 4: Using Docker
```bash
# Build and run with Docker Compose
docker-compose -f config/docker-compose.yml up --build

# Or build and run manually
docker build -f config/Dockerfile -t trip-tracker .
docker run -p 8001:8000 trip-tracker
```

## ⚡ Quick Command Reference

```bash
# 🚀 Start the API server
cd src && python3 main.py

# 🧪 Test the API
python3 scripts/test_api.py

# 💚 Check server health
curl http://localhost:8001/health

# 📖 Open API documentation
# Visit: http://localhost:8001/docs

# 🛑 Stop all uvicorn processes
pkill -f "uvicorn"
```

## 📡 API Endpoints

The API is available at: **http://localhost:8001**

### Interactive Documentation
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Core Endpoints

#### Authentication (`/api/v1/auth/`)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get access token
- `GET /api/v1/auth/me` - Get current user info

#### Trip Management (`/api/v1/trips/`)
- `POST /api/v1/trips/start` - Start a new trip
- `POST /api/v1/trips/update` - Update trip with location data
- `POST /api/v1/trips/stop` - Stop current trip
- `GET /api/v1/trips` - Get trip history
- `GET /api/v1/trips/active` - Get current active trip
- `GET /api/v1/trips/{trip_id}` - Get specific trip

#### Geofences (`/api/v1/geofences/`)
- `POST /api/v1/geofences` - Create geofence
- `GET /api/v1/geofences` - Get user's geofences

#### Settings (`/api/v1/settings/`)
- `GET /api/v1/settings` - Get user settings
- `PUT /api/v1/settings` - Update user settings

#### Utility
- `GET /health` - Health check
- `GET /` - API information

## 🧪 Testing the API

### 1. Register a User
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8001/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure123"
```

### 3. Start a Trip
```bash
curl -X POST "http://localhost:8001/api/v1/trips/start" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7749,
    "longitude": -122.4194,
    "title": "Morning Commute",
    "description": "Drive to work"
  }'
```

### 4. Update Trip Location
```bash
curl -X POST "http://localhost:8001/api/v1/trips/update" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 37.7849,
    "longitude": -122.4094,
    "speed": 45.5,
    "accuracy": 5.0
  }'
```

## 🏗️ Architecture

### Database Models
- **Users**: User accounts and authentication
- **Trips**: Trip sessions with start/end times and locations
- **TripPoints**: GPS coordinates collected during trips
- **Geofences**: Geographic boundaries for auto-stop functionality
- **UserSettings**: User preferences and configuration

### Key Features
- **JWT Authentication**: Secure token-based authentication
- **Real-time Location Tracking**: GPS coordinates with timestamps
- **Geofencing**: Automatic trip stopping in designated areas
- **Distance Calculation**: Haversine formula for accurate distance
- **User Settings**: Configurable behavior and preferences

## 🔧 Development

### Project Organization
- **Clean Structure**: Organized source code in `src/` directory
- **Configuration Management**: All config files in `config/` directory  
- **Data Separation**: Database and data files in `data/` directory
- **Documentation**: Comprehensive docs in `docs/` directory
- **Utility Scripts**: Setup and testing scripts in `scripts/` directory

### Key Features
- **Modular Structure**: Separated concerns with clear module boundaries
- **Type Safety**: Pydantic schemas for request/response validation
- **Database**: SQLAlchemy ORM with SQLite for development
- **API Documentation**: Auto-generated with FastAPI
- **Error Handling**: Comprehensive HTTP error responses

### Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp config/.env.example .env

# Edit .env file with your settings
nano .env
```

### Running Tests
```bash
# Run API tests
python3 scripts/test_api.py

# Manual health check
curl http://localhost:8001/health

# Test individual endpoints
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "test123"}'
```

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Error: address already in use
# Solution: Kill existing processes or use different port
pkill -f "uvicorn"
# Or use different port
cd src && uvicorn main:app --host 127.0.0.1 --port 8002
```

#### File Watch Limit Reached
```bash
# Error: OS file watch limit reached
# Solution: Run without reload
cd src && uvicorn main:app --host 127.0.0.1 --port 8001
# (Remove --reload flag)
```

#### Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure you're in the src directory
cd src && python3 main.py
# Or install missing dependencies
pip install email-validator
```

#### Database Issues
```bash
# Error: Database connection issues
# Solution: Check data directory exists and has write permissions
mkdir -p data
chmod 755 data
```

### Getting Help
- 📖 **API Documentation**: http://localhost:8001/docs
- 🔍 **Alternative Docs**: http://localhost:8001/redoc  
- 💚 **Health Check**: http://localhost:8001/health
- 🏠 **Root Info**: http://localhost:8001/

## 🚦 Next Steps (Phase 2)

- [ ] WebSocket support for real-time updates
- [ ] Mobile app development (React Native/Flutter)
- [ ] Advanced analytics and reporting
- [ ] Data export (GPX, KML formats)
- [ ] Social features and trip sharing
- [ ] Offline mode support
- [ ] Push notifications
- [ ] Multiple vehicle support

## 📝 License

MIT License - see LICENSE file for details.

---

**Built with FastAPI, SQLAlchemy, and SQLite** 🐍⚡