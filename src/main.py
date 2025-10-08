#!/usr/bin/env python3
"""
Smart Car Trip Tracker - Main Application Entry Point
A personal car trip diary that tracks trips with GPS, auto-stops at geofences, and syncs securely.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import uvicorn

# Import local modules (using relative imports that work)
from database import get_db, create_tables
from schemas import *
from crud import *
from auth import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Create FastAPI app
app = FastAPI(
    title="Smart Car Trip Tracker API",
    description="A personal car trip diary that tracks trips with GPS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web/mobile app integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.post("/api/v1/auth/register", response_model=User, tags=["Authentication"])
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_user(db=db, user=user)

@app.post("/api/v1/auth/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# ============================================================================
# TRIP ROUTES
# ============================================================================

@app.post("/api/v1/trips/start", response_model=Trip, tags=["Trips"])
async def start_trip(
    trip_data: TripStart, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new trip."""
    # Check if user has an active trip
    active_trip = get_active_trip(db, current_user.id)
    if active_trip:
        raise HTTPException(status_code=400, detail="User already has an active trip")
    
    # Check for geofence triggers
    geofences = check_geofence_trigger(db, current_user.id, trip_data.latitude, trip_data.longitude)
    for geofence in geofences:
        if geofence.action == "stop":
            raise HTTPException(status_code=400, detail=f"Cannot start trip in stop geofence: {geofence.name}")
    
    return create_trip(db=db, trip=trip_data, user_id=current_user.id)

@app.post("/api/v1/trips/update", tags=["Trips"])
async def update_trip(
    location_data: TripUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current trip with new location data."""
    active_trip = get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    
    # Check for geofence triggers
    geofences = check_geofence_trigger(db, current_user.id, location_data.latitude, location_data.longitude)
    user_settings = get_user_settings(db, current_user.id)
    
    for geofence in geofences:
        if geofence.action == "stop" and user_settings and user_settings.auto_stop_at_geofences:
            # Auto-stop the trip
            stop_data = TripStop(latitude=location_data.latitude, longitude=location_data.longitude)
            stop_trip(db, active_trip.id, stop_data)
            return {"message": f"Trip automatically stopped at geofence: {geofence.name}"}
    
    trip_point = update_trip_location(db, active_trip.id, location_data)
    return {"message": "Location updated successfully", "trip_point_id": trip_point.id}

@app.post("/api/v1/trips/stop", response_model=Trip, tags=["Trips"])
async def stop_trip_endpoint(
    stop_data: TripStop,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop the current active trip."""
    active_trip = get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    
    return stop_trip(db, active_trip.id, stop_data)

@app.get("/api/v1/trips", response_model=List[Trip], tags=["Trips"])
async def get_trips_endpoint(
    skip: int = 0, 
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's trip history."""
    trips = get_trips(db, user_id=current_user.id, skip=skip, limit=limit)
    return trips

@app.get("/api/v1/trips/active", response_model=Trip, tags=["Trips"])
async def get_active_trip_endpoint(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active trip."""
    active_trip = get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    return active_trip

@app.get("/api/v1/trips/{trip_id}", response_model=Trip, tags=["Trips"])
async def get_trip_endpoint(
    trip_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific trip by ID."""
    trip = get_trip(db, trip_id=trip_id, user_id=current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

# ============================================================================
# GEOFENCE ROUTES
# ============================================================================

@app.post("/api/v1/geofences", response_model=Geofence, tags=["Geofences"])
async def create_geofence_endpoint(
    geofence: GeofenceCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new geofence."""
    return create_geofence(db=db, geofence=geofence, user_id=current_user.id)

@app.get("/api/v1/geofences", response_model=List[Geofence], tags=["Geofences"])
async def get_geofences_endpoint(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's geofences."""
    return get_geofences(db, user_id=current_user.id)

# ============================================================================
# SETTINGS ROUTES
# ============================================================================

@app.get("/api/v1/settings", response_model=UserSettings, tags=["Settings"])
async def get_settings_endpoint(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings."""
    settings = get_user_settings(db, current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@app.put("/api/v1/settings", response_model=UserSettings, tags=["Settings"])
async def update_settings_endpoint(
    settings: UserSettingsCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings."""
    return update_user_settings(db, current_user.id, settings)

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "message": "Smart Car Trip Tracker API is running",
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Smart Car Trip Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "authentication": "/api/v1/auth/",
            "trips": "/api/v1/trips/",
            "geofences": "/api/v1/geofences/",
            "settings": "/api/v1/settings/"
        }
    }

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )