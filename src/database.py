from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# SQLite database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///../data/trip_tracker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = relationship("Trip", back_populates="user")
    geofences = relationship("Geofence", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_latitude = Column(Float, nullable=False)
    start_longitude = Column(Float, nullable=False)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    total_distance = Column(Float, default=0.0)  # in kilometers
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trips")
    trip_points = relationship("TripPoint", back_populates="trip", cascade="all, delete-orphan")

class TripPoint(Base):
    __tablename__ = "trip_points"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)  # in km/h
    accuracy = Column(Float, nullable=True)  # in meters
    timestamp = Column(DateTime, nullable=False)
    
    # Relationships
    trip = relationship("Trip", back_populates="trip_points")

class Geofence(Base):
    __tablename__ = "geofences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)  # in meters
    action = Column(String(20), default="stop")  # stop, start, notify
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="geofences")

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    auto_start_trips = Column(Boolean, default=False)
    auto_stop_at_geofences = Column(Boolean, default=True)
    location_update_interval = Column(Integer, default=30)  # seconds
    distance_threshold = Column(Float, default=0.01)  # km
    enable_notifications = Column(Boolean, default=True)
    sync_method = Column(String(20), default="cloud")  # cloud, lan, manual
    
    # Relationships
    user = relationship("User", back_populates="settings")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)