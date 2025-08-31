# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    gender = Column(String(50)) # Bisa diubah ke Enum jika ada pilihan terbatas
    birthdate = Column(DateTime)
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    activity_level = Column(String(50)) # Bisa diubah ke Enum
    created_at = Column(DateTime, default=datetime.utcnow)
    profile_complete = Column(Boolean, default=False) # Menambahkan status kelengkapan profil

    nutrition_targets = relationship("NutritionTarget", back_populates="user", uselist=False)
    consumptions = relationship("Consumption", back_populates="user")
    spectra = relationship("Spectra", back_populates="user")
    reports = relationship("Report", back_populates="user")

class NutritionTarget(Base):
    __tablename__ = "nutrition_targets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    daily_calorie = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="nutrition_targets")

class FoodSource(enum.Enum):
    internal = "internal"
    ml = "ml"

class Food(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    brand = Column(String(255), nullable=True)
    per_unit_g = Column(Float, nullable=True) # Gram per unit (misal: 1 telur = 50g)
    kcal_per_100g = Column(Float)
    protein_g_per_100g = Column(Float)
    carbs_g_per_100g = Column(Float)
    fat_g_per_100g = Column(Float)
    source = Column(Enum(FoodSource))

class Consumption(Base):
    __tablename__ = "consumptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    weight_g = Column(Float)
    eaten_at = Column(DateTime) # TZ aware
    kcal = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="consumptions")
    food = relationship("Food")

class Spectra(Base):
    __tablename__ = "spectra"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wavelengths_json = Column(JSON) # Simpan sebagai JSON string
    absorbance_json = Column(JSON) # Simpan sebagai JSON string
    measured_at = Column(DateTime)
    sample_note = Column(Text, nullable=True)

    user = relationship("User", back_populates="spectra")
    ml_predictions = relationship("MLPrediction", back_populates="spectra")

class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    id = Column(Integer, primary_key=True, index=True)
    spectra_id = Column(Integer, ForeignKey("spectra.id"))
    predicted_kcal = Column(Float)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    model_version = Column(String(255))
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    spectra = relationship("Spectra", back_populates="ml_predictions")

class ReportRangeType(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    range_type = Column(Enum(ReportRangeType))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    pdf_path = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reports")

