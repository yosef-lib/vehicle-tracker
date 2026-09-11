from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    telegram_id = Column(String, unique=True, nullable=True)

    vehicles = relationship("Vehicle", back_populates="owner")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)  # e.g., "Vario 150"
    type = Column(String) # e.g., "Motor", "Mobil"
    license_plate = Column(String)

    owner = relationship("User", back_populates="vehicles")
    fuel_logs = relationship("FuelLog", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle", cascade="all, delete-orphan")
    daily_logs = relationship("DailyLog", back_populates="vehicle", cascade="all, delete-orphan")

class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    date = Column(Date, index=True)
    odometer = Column(Integer)
    fuel_type = Column(String) # Pertamax, Pertalite
    volume_liters = Column(Float)
    cost = Column(Float)
    is_full = Column(Boolean, default=True)

    vehicle = relationship("Vehicle", back_populates="fuel_logs")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    date = Column(Date, index=True)
    category = Column(String) # "Oli", "Sparepart", "Pajak"
    description = Column(String)
    odometer = Column(Integer, nullable=True)
    cost = Column(Float)

    vehicle = relationship("Vehicle", back_populates="maintenance_logs")

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    date = Column(Date, index=True)
    odometer = Column(Integer)
    fuel_indicator = Column(String) # e.g., "2 bar"

    vehicle = relationship("Vehicle", back_populates="daily_logs")
