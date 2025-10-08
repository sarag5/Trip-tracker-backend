from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import math

import database
import schemas
import auth

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = database.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default settings for new user
    create_user_settings(db, schemas.UserSettingsCreate(), db_user.id)
    
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

# Trip CRUD operations
def create_trip(db: Session, trip: schemas.TripStart, user_id: int):
    db_trip = database.Trip(
        user_id=user_id,
        title=trip.title,
        description=trip.description,
        start_time=datetime.utcnow(),
        start_latitude=trip.latitude,
        start_longitude=trip.longitude,
        is_active=True
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    
    # Add first trip point
    first_point = database.TripPoint(
        trip_id=db_trip.id,
        latitude=trip.latitude,
        longitude=trip.longitude,
        timestamp=db_trip.start_time
    )
    db.add(first_point)
    db.commit()
    
    return db_trip

def get_active_trip(db: Session, user_id: int):
    return db.query(database.Trip).filter(
        database.Trip.user_id == user_id,
        database.Trip.is_active == True
    ).first()

def get_trips(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(database.Trip).filter(
        database.Trip.user_id == user_id
    ).offset(skip).limit(limit).all()

def get_trip(db: Session, trip_id: int, user_id: int):
    return db.query(database.Trip).filter(
        database.Trip.id == trip_id,
        database.Trip.user_id == user_id
    ).first()

def update_trip_location(db: Session, trip_id: int, location: schemas.TripUpdate):
    # Add new trip point
    trip_point = database.TripPoint(
        trip_id=trip_id,
        latitude=location.latitude,
        longitude=location.longitude,
        altitude=location.altitude,
        speed=location.speed,
        accuracy=location.accuracy,
        timestamp=datetime.utcnow()
    )
    db.add(trip_point)
    
    # Update trip distance
    trip = db.query(database.Trip).filter(database.Trip.id == trip_id).first()
    if trip:
        last_point = db.query(database.TripPoint).filter(
            database.TripPoint.trip_id == trip_id
        ).order_by(database.TripPoint.timestamp.desc()).offset(1).first()
        
        if last_point:
            distance = calculate_distance(
                last_point.latitude, last_point.longitude,
                location.latitude, location.longitude
            )
            trip.total_distance += distance
    
    db.commit()
    return trip_point

def stop_trip(db: Session, trip_id: int, location: schemas.TripStop):
    trip = db.query(database.Trip).filter(database.Trip.id == trip_id).first()
    if trip:
        trip.end_time = datetime.utcnow()
        trip.end_latitude = location.latitude
        trip.end_longitude = location.longitude
        trip.is_active = False
        
        # Add final trip point
        final_point = database.TripPoint(
            trip_id=trip_id,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=trip.end_time
        )
        db.add(final_point)
        db.commit()
        
    return trip

# Geofence CRUD operations
def create_geofence(db: Session, geofence: schemas.GeofenceCreate, user_id: int):
    db_geofence = database.Geofence(
        user_id=user_id,
        name=geofence.name,
        description=geofence.description,
        latitude=geofence.latitude,
        longitude=geofence.longitude,
        radius=geofence.radius,
        action=geofence.action
    )
    db.add(db_geofence)
    db.commit()
    db.refresh(db_geofence)
    return db_geofence

def get_geofences(db: Session, user_id: int):
    return db.query(database.Geofence).filter(
        database.Geofence.user_id == user_id,
        database.Geofence.is_active == True
    ).all()

def check_geofence_trigger(db: Session, user_id: int, latitude: float, longitude: float):
    geofences = get_geofences(db, user_id)
    triggered_geofences = []
    
    for geofence in geofences:
        distance = calculate_distance(
            latitude, longitude,
            geofence.latitude, geofence.longitude
        ) * 1000  # Convert to meters
        
        if distance <= geofence.radius:
            triggered_geofences.append(geofence)
    
    return triggered_geofences

# Settings CRUD operations
def create_user_settings(db: Session, settings: schemas.UserSettingsCreate, user_id: int):
    db_settings = database.UserSettings(
        user_id=user_id,
        auto_start_trips=settings.auto_start_trips,
        auto_stop_at_geofences=settings.auto_stop_at_geofences,
        location_update_interval=settings.location_update_interval,
        distance_threshold=settings.distance_threshold,
        enable_notifications=settings.enable_notifications,
        sync_method=settings.sync_method
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def get_user_settings(db: Session, user_id: int):
    return db.query(database.UserSettings).filter(
        database.UserSettings.user_id == user_id
    ).first()

def update_user_settings(db: Session, user_id: int, settings: schemas.UserSettingsCreate):
    db_settings = get_user_settings(db, user_id)
    if db_settings:
        for key, value in settings.dict().items():
            setattr(db_settings, key, value)
        db.commit()
        db.refresh(db_settings)
    return db_settings

# Utility functions
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c