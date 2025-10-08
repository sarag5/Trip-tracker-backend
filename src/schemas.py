from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Trip schemas
class TripPointBase(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime

class TripPointCreate(TripPointBase):
    pass

class TripPoint(TripPointBase):
    id: int
    trip_id: int
    
    class Config:
        from_attributes = True

class TripBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TripStart(BaseModel):
    latitude: float
    longitude: float
    title: Optional[str] = None
    description: Optional[str] = None

class TripUpdate(BaseModel):
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    accuracy: Optional[float] = None

class TripStop(BaseModel):
    latitude: float
    longitude: float

class Trip(TripBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    start_latitude: float
    start_longitude: float
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    total_distance: float
    is_active: bool
    created_at: datetime
    trip_points: List[TripPoint] = []
    
    class Config:
        from_attributes = True

# Geofence schemas
class GeofenceBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    radius: float
    action: str = "stop"

class GeofenceCreate(GeofenceBase):
    pass

class Geofence(GeofenceBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Settings schemas
class UserSettingsBase(BaseModel):
    auto_start_trips: bool = False
    auto_stop_at_geofences: bool = True
    location_update_interval: int = 30
    distance_threshold: float = 0.01
    enable_notifications: bool = True
    sync_method: str = "cloud"

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettings(UserSettingsBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None