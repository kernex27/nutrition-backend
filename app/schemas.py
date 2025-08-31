# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import enum

# --- Auth Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level: Optional[str] = None
    profile_complete: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    profile_complete: bool = False # Menambahkan status kelengkapan profil

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

# --- Nutrition Target Schemas ---
class NutritionTargetBase(BaseModel):
    daily_calorie: int
    protein_g: float
    carbs_g: float
    fat_g: float

class NutritionTargetCreate(NutritionTargetBase):
    pass

class NutritionTarget(NutritionTargetBase):
    id: int
    user_id: int
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Food Schemas ---
class FoodSourceEnum(str, enum.Enum):
    internal = "internal"
    ml = "ml"

class FoodBase(BaseModel):
    name: str
    brand: Optional[str] = None
    per_unit_g: Optional[float] = None
    kcal_per_100g: float
    protein_g_per_100g: float
    carbs_g_per_100g: float
    fat_g_per_100g: float
    source: FoodSourceEnum = FoodSourceEnum.internal

class FoodCreate(FoodBase):
    pass

class Food(FoodBase):
    id: int

    class Config:
        orm_mode = True

# --- Consumption Schemas ---
class ConsumptionBase(BaseModel):
    food_id: int
    weight_g: float
    eaten_at: datetime
    note: Optional[str] = None

class ConsumptionCreate(ConsumptionBase):
    # Kcal, protein, carbs, fat akan dihitung di backend
    pass

class ConsumptionUpdate(BaseModel):
    food_id: Optional[int] = None
    weight_g: Optional[float] = None
    eaten_at: Optional[datetime] = None
    note: Optional[str] = None
    kcal: Optional[float] = None # Untuk update dari ML atau re-kalkulasi
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None

class Consumption(ConsumptionBase):
    id: int
    user_id: int
    kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    created_at: datetime

    class Config:
        orm_mode = True

# --- Spectra & ML Schemas ---
class SpectraBase(BaseModel):
    wavelengths_json: List[float] # Akan disimpan sebagai JSON string di DB
    absorbance_json: List[float] # Akan disimpan sebagai JSON string di DB
    measured_at: datetime
    sample_note: Optional[str] = None

class SpectraCreate(SpectraBase):
    pass

class Spectra(SpectraBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class MLPredictionRequest(BaseModel):
    wavelengths: List[float]
    absorbance: List[float]
    path_length_cm: float
    molar_absorptivity: Optional[float] = None
    model_features: Optional[Dict[str, Any]] = None

class MLPredictionBase(BaseModel):
    spectra_id: int
    predicted_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    model_version: str
    quality_score: Optional[float] = None

class MLPredictionCreate(MLPredictionBase):
    pass

class MLPrediction(MLPredictionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Dashboard Schemas ---
class MacroPercentage(BaseModel):
    name: str
    value: float

class KcalByHour(BaseModel):
    hour: str
    kcal: float

class DashboardSummary(BaseModel):
    total_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    macro_pct: List[MacroPercentage]
    by_hour: List[KcalByHour]

# --- Report Schemas ---
class ReportRangeTypeEnum(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class ReportBase(BaseModel):
    range_type: ReportRangeTypeEnum
    start_date: date
    end_date: date
    pdf_path: str

class ReportGenerate(BaseModel):
    range_type: ReportRangeTypeEnum
    start_date: date
    end_date: date

class ReportCreate(ReportBase):
    pass

class Report(ReportBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- AI Assistant Schemas ---
class AIRecommendationRequest(BaseModel):
    deficit_calorie: float
    recent_consumptions: List[Dict[str, Any]] # Bisa lebih spesifik jika perlu
    targets: Dict[str, Any] # Bisa lebih spesifik jika perlu

class AIRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]] # Akan berisi tabel rekomendasi

