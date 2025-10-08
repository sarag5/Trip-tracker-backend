from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import database
import schemas
import crud
import auth

# Create FastAPI app
app = FastAPI(
    title="Smart Car Trip Tracker API",
    description="A personal car trip diary that tracks trips with GPS",
    version="1.0.0"
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create database tables
database.create_tables()

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = auth.verify_token(token, credentials_exception)
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Authentication endpoints
@app.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Login and get access token."""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: database.User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# Trip endpoints
@app.post("/trip/start", response_model=schemas.Trip)
async def start_trip(
    trip_data: schemas.TripStart, 
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Start a new trip."""
    # Check if user has an active trip
    active_trip = crud.get_active_trip(db, current_user.id)
    if active_trip:
        raise HTTPException(status_code=400, detail="User already has an active trip")
    
    # Check for geofence triggers
    geofences = crud.check_geofence_trigger(db, current_user.id, trip_data.latitude, trip_data.longitude)
    for geofence in geofences:
        if geofence.action == "stop":
            raise HTTPException(status_code=400, detail=f"Cannot start trip in stop geofence: {geofence.name}")
    
    return crud.create_trip(db=db, trip=trip_data, user_id=current_user.id)

@app.post("/trip/update")
async def update_trip(
    location_data: schemas.TripUpdate,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Update current trip with new location data."""
    active_trip = crud.get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    
    # Check for geofence triggers
    geofences = crud.check_geofence_trigger(db, current_user.id, location_data.latitude, location_data.longitude)
    user_settings = crud.get_user_settings(db, current_user.id)
    
    for geofence in geofences:
        if geofence.action == "stop" and user_settings and user_settings.auto_stop_at_geofences:
            # Auto-stop the trip
            stop_data = schemas.TripStop(latitude=location_data.latitude, longitude=location_data.longitude)
            crud.stop_trip(db, active_trip.id, stop_data)
            return {"message": f"Trip automatically stopped at geofence: {geofence.name}"}
    
    trip_point = crud.update_trip_location(db, active_trip.id, location_data)
    return {"message": "Location updated successfully", "trip_point_id": trip_point.id}

@app.post("/trip/stop", response_model=schemas.Trip)
async def stop_trip(
    stop_data: schemas.TripStop,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Stop the current active trip."""
    active_trip = crud.get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    
    return crud.stop_trip(db, active_trip.id, stop_data)

@app.get("/trips", response_model=List[schemas.Trip])
async def get_trips(
    skip: int = 0, 
    limit: int = 100,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get user's trip history."""
    trips = crud.get_trips(db, user_id=current_user.id, skip=skip, limit=limit)
    return trips

@app.get("/trip/active", response_model=schemas.Trip)
async def get_active_trip(
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get current active trip."""
    active_trip = crud.get_active_trip(db, current_user.id)
    if not active_trip:
        raise HTTPException(status_code=404, detail="No active trip found")
    return active_trip

@app.get("/trip/{trip_id}", response_model=schemas.Trip)
async def get_trip(
    trip_id: int,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get specific trip by ID."""
    trip = crud.get_trip(db, trip_id=trip_id, user_id=current_user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

# Geofence endpoints
@app.post("/geofences", response_model=schemas.Geofence)
async def create_geofence(
    geofence: schemas.GeofenceCreate,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Create a new geofence."""
    return crud.create_geofence(db=db, geofence=geofence, user_id=current_user.id)

@app.get("/geofences", response_model=List[schemas.Geofence])
async def get_geofences(
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get user's geofences."""
    return crud.get_geofences(db, user_id=current_user.id)

# Settings endpoints
@app.get("/settings", response_model=schemas.UserSettings)
async def get_settings(
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get user settings."""
    settings = crud.get_user_settings(db, current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@app.put("/settings", response_model=schemas.UserSettings)
async def update_settings(
    settings: schemas.UserSettingsCreate,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Update user settings."""
    return crud.update_user_settings(db, current_user.id, settings)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Smart Car Trip Tracker API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)