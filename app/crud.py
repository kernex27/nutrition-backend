# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Optional

from app import models, schemas, auth

# --- CRUD for User ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        gender=user.gender,
        birthdate=user.birthdate,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        profile_complete=True if user.gender and user.birthdate and user.height_cm and user.weight_kg and user.activity_level else False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, current_user: models.User, user_update: schemas.UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    # Perbarui profile_complete jika semua data penting sudah ada
    if (current_user.gender and current_user.birthdate and 
        current_user.height_cm and current_user.weight_kg and 
        current_user.activity_level):
        current_user.profile_complete = True
    else:
        current_user.profile_complete = False

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

# --- CRUD for NutritionTarget ---
def get_nutrition_targets(db: Session, user_id: int):
    return db.query(models.NutritionTarget).filter(models.NutritionTarget.user_id == user_id).first()

def update_or_create_nutrition_targets(db: Session, user_id: int, targets_data: schemas.NutritionTargetCreate):
    db_targets = get_nutrition_targets(db, user_id)
    if db_targets:
        for key, value in targets_data.dict().items():
            setattr(db_targets, key, value)
        db_targets.updated_at = datetime.utcnow()
    else:
        db_targets = models.NutritionTarget(**targets_data.dict(), user_id=user_id)
    db.add(db_targets)
    db.commit()
    db.refresh(db_targets)
    return db_targets

# --- CRUD for Food ---
def get_foods(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Food)
    if search:
        query = query.filter(models.Food.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_food_by_id(db: Session, food_id: int):
    return db.query(models.Food).filter(models.Food.id == food_id).first()

def create_food(db: Session, food: schemas.FoodCreate):
    db_food = models.Food(**food.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

# --- CRUD for Consumption ---
def get_consumptions(db: Session, user_id: int, from_date: Optional[str] = None, to_date: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Consumption).filter(models.Consumption.user_id == user_id)
    if from_date:
        query = query.filter(models.Consumption.eaten_at >= from_date)
    if to_date:
        # Tambahkan 1 hari untuk mencakup seluruh tanggal 'to_date'
        end_of_day = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(models.Consumption.eaten_at < end_of_day)
    return query.offset(skip).limit(limit).all()

def get_consumption(db: Session, consumption_id: int):
    return db.query(models.Consumption).filter(models.Consumption.id == consumption_id).first()

def create_consumption(db: Session, user_id: int, consumption: schemas.ConsumptionCreate, kcal: float, protein_g: float, carbs_g: float, fat_g: float):
    db_consumption = models.Consumption(
        **consumption.dict(), 
        user_id=user_id, 
        kcal=kcal, 
        protein_g=protein_g, 
        carbs_g=carbs_g, 
        fat_g=fat_g
    )
    db.add(db_consumption)
    db.commit()
    db.refresh(db_consumption)
    return db_consumption

def update_consumption(db: Session, db_consumption: models.Consumption, consumption_update: schemas.ConsumptionUpdate):
    update_data = consumption_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_consumption, key, value)
    db.add(db_consumption)
    db.commit()
    db.refresh(db_consumption)
    return db_consumption

def delete_consumption(db: Session, db_consumption: models.Consumption):
    db.delete(db_consumption)
    db.commit()

# --- CRUD for Spectra ---
def create_spectra(db: Session, user_id: int, spectra: schemas.SpectraCreate):
    db_spectra = models.Spectra(**spectra.dict(), user_id=user_id)
    db.add(db_spectra)
    db.commit()
    db.refresh(db_spectra)
    return db_spectra

# --- CRUD for MLPrediction ---
def create_ml_prediction(db: Session, spectra_id: int, predicted_kcal: float, protein_g: float, carbs_g: float, fat_g: float, model_version: str, quality_score: Optional[float] = None):
    db_prediction = models.MLPrediction(
        spectra_id=spectra_id,
        predicted_kcal=predicted_kcal,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        model_version=model_version,
        quality_score=quality_score
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

# --- CRUD for Reports ---
def get_reports(db: Session, user_id: int, range_type: str, start_date: str, end_date: str):
    query = db.query(models.Report).filter(models.Report.user_id == user_id)
    if range_type:
        query = query.filter(models.Report.range_type == range_type)
    if start_date:
        query = query.filter(models.Report.start_date >= start_date)
    if end_date:
        end_of_day = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(models.Report.end_date < end_of_day)
    return query.all()

def create_report(db: Session, user_id: int, range_type: str, start_date: date, end_date: date, pdf_path: str):
    db_report = models.Report(
        user_id=user_id,
        range_type=range_type,
        start_date=start_date,
        end_date=end_date,
        pdf_path=pdf_path
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

