# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uvicorn
import redis.asyncio as redis
from socketio import AsyncServer, ASGIApp
from typing import List, Dict, Any
from app.database import engine, Base, get_db
from app import models, schemas, auth, crud, ml_utils, pdf_utils
from app.config import settings




# Inisialisasi Database
Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI(
    title="NIRMAS - Nutritional Recommendation Apps API",
    description="API untuk memantau konsumsi gizi harian, rekomendasi AI, dan laporan.",
    version="1.0.0",
)

# Inisialisasi Socket.IO
sio = AsyncServer(async_mode='asgi', cors_allowed_origins="*")
socket_app = ASGIApp(sio, other_asgi_app=app)

# Redis Client (untuk cache/queue)
# redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# OAuth2PasswordBearer untuk Autentikasi
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency untuk mendapatkan user saat ini
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = auth.verify_access_token(token, credentials_exception)
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user

# --- Socket.IO Events ---
@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")
    # Anda bisa menyimpan sid dan user_id di sini untuk mapping
    # Misalnya: sio.enter_room(sid, f"user:{auth['user_id']}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

# --- API Endpoints ---

# Auth Router
@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)

@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_access_token(current_user: models.User = Depends(get_current_user)):
    # Implementasi refresh token (opsional, bisa melibatkan refresh token di DB)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = auth.create_access_token(
        data={"sub": current_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

# User Profile/Targets Router
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_users_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.update_user(db, current_user, user_update)

@app.get("/users/me/targets", response_model=schemas.NutritionTarget)
def get_my_nutrition_targets(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    targets = crud.get_nutrition_targets(db, user_id=current_user.id)
    if not targets:
        raise HTTPException(status_code=404, detail="Nutrition targets not set for this user")
    return targets

@app.put("/users/me/targets", response_model=schemas.NutritionTarget)
def update_my_nutrition_targets(targets_update: schemas.NutritionTargetCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.update_or_create_nutrition_targets(db, user_id=current_user.id, targets_data=targets_update)

# Foods Router
@app.get("/foods", response_model=List[schemas.Food])
def search_foods(search: str = None, db: Session = Depends(get_db)):
    return crud.get_foods(db, search=search)

@app.post("/foods", response_model=schemas.Food)
def create_food(food: schemas.FoodCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Hanya admin atau user tertentu yang bisa menambah custom food
    # Untuk demo, kita izinkan semua user terautentikasi
    return crud.create_food(db, food=food)

@app.get("/foods/{food_id}", response_model=schemas.Food)
def get_food(food_id: int, db: Session = Depends(get_db)):
    db_food = crud.get_food_by_id(db, food_id=food_id)
    if not db_food:
        raise HTTPException(status_code=404, detail="Food not found")
    return db_food

# Consumptions Router
@app.get("/consumptions", response_model=List[schemas.Consumption])
def get_consumptions(from_date: str = None, to_date: str = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Implementasi filter tanggal
    return crud.get_consumptions(db, user_id=current_user.id, from_date=from_date, to_date=to_date)

@app.post("/consumptions", response_model=schemas.Consumption)
def create_consumption(consumption: schemas.ConsumptionCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Di sini Anda akan melakukan perhitungan kcal, protein, dll. berdasarkan food_id dan weight_g
    # Untuk demo, kita asumsikan sudah ada di schema atau dihitung dummy
    food = crud.get_food_by_id(db, consumption.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    
    # Contoh perhitungan dummy berdasarkan 100g data
    kcal = (food.kcal_per_100g / 100) * consumption.weight_g
    protein = (food.protein_g_per_100g / 100) * consumption.weight_g
    carbs = (food.carbs_g_per_100g / 100) * consumption.weight_g
    fat = (food.fat_g_per_100g / 100) * consumption.weight_g

    db_consumption = crud.create_consumption(
        db=db, 
        user_id=current_user.id, 
        consumption=consumption,
        kcal=kcal, protein_g=protein, carbs_g=carbs, fat_g=fat
    )
    # Emit Socket.IO event
    sio.emit(f"user:{current_user.id}:consumptions", {"event": "consumption:created", "payload": schemas.Consumption.from_orm(db_consumption).dict()})
    sio.emit(f"user:{current_user.id}:dashboard", {"event": "dashboard:summary", "payload": {"message": "Dashboard needs refresh"}})
    return db_consumption

@app.put("/consumptions/{consumption_id}", response_model=schemas.Consumption)
def update_consumption(consumption_id: int, consumption_update: schemas.ConsumptionUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_consumption = crud.get_consumption(db, consumption_id=consumption_id)
    if not db_consumption or db_consumption.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Consumption not found or not authorized")
    
    # Re-calculate nutrition if weight_g or food_id changes
    if consumption_update.food_id and consumption_update.food_id != db_consumption.food_id:
        food = crud.get_food_by_id(db, consumption_update.food_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        weight_g = consumption_update.weight_g if consumption_update.weight_g else db_consumption.weight_g
        consumption_update.kcal = (food.kcal_per_100g / 100) * weight_g
        consumption_update.protein_g = (food.protein_g_per_100g / 100) * weight_g
        consumption_update.carbs_g = (food.carbs_g_per_100g / 100) * weight_g
        consumption_update.fat_g = (food.fat_g_per_100g / 100) * weight_g
    elif consumption_update.weight_g and consumption_update.weight_g != db_consumption.weight_g:
        food = crud.get_food_by_id(db, db_consumption.food_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        consumption_update.kcal = (food.kcal_per_100g / 100) * consumption_update.weight_g
        consumption_update.protein_g = (food.protein_g_per_100g / 100) * consumption_update.weight_g
        consumption_update.carbs_g = (food.carbs_g_per_100g / 100) * consumption_update.weight_g
        consumption_update.fat_g = (food.fat_g_per_100g / 100) * consumption_update.weight_g


    updated_consumption = crud.update_consumption(db, db_consumption, consumption_update)
    sio.emit(f"user:{current_user.id}:consumptions", {"event": "consumption:updated", "payload": schemas.Consumption.from_orm(updated_consumption).dict()})
    sio.emit(f"user:{current_user.id}:dashboard", {"event": "dashboard:summary", "payload": {"message": "Dashboard needs refresh"}})
    return updated_consumption

@app.delete("/consumptions/{consumption_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consumption(consumption_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_consumption = crud.get_consumption(db, consumption_id=consumption_id)
    if not db_consumption or db_consumption.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Consumption not found or not authorized")
    crud.delete_consumption(db, db_consumption)
    sio.emit(f"user:{current_user.id}:consumptions", {"event": "consumption:deleted", "payload": {"id": consumption_id}})
    sio.emit(f"user:{current_user.id}:dashboard", {"event": "dashboard:summary", "payload": {"message": "Dashboard needs refresh"}})
    return

# Spectra & ML Router
@app.post("/spectra", response_model=schemas.Spectra)
def create_spectra(spectra: schemas.SpectraCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_spectra(db, user_id=current_user.id, spectra=spectra)

@app.post("/ml/predict", response_model=schemas.MLPrediction)
def predict_nutrition_from_spectra(
    prediction_request: schemas.MLPredictionRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Simulasikan proses ML
    predicted_data = ml_utils.simulate_ml_prediction(
        prediction_request.wavelengths,
        prediction_request.absorbance,
        prediction_request.path_length_cm,
        prediction_request.molar_absorptivity,
        prediction_request.model_features
    )
    
    # Simpan hasil prediksi ke database
    spectra_data = schemas.SpectraCreate(
        wavelengths_json=prediction_request.wavelengths,
        absorbance_json=prediction_request.absorbance,
        measured_at=datetime.now(),
        sample_note="Auto-generated from ML prediction request"
    )
    db_spectra = crud.create_spectra(db, user_id=current_user.id, spectra=spectra_data)

    db_prediction = crud.create_ml_prediction(
        db,
        spectra_id=db_spectra.id,
        predicted_kcal=predicted_data["predicted_kcal"],
        protein_g=predicted_data["protein_g"],
        carbs_g=predicted_data["carbs_g"],
        fat_g=predicted_data["fat_g"],
        model_version=predicted_data["model_version"],
        quality_score=predicted_data["quality_score"]
    )
    return db_prediction

# Dashboard Router
@app.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(date: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    consumptions_today = crud.get_consumptions(db, user_id=current_user.id, from_date=date, to_date=date)
    
    total_kcal = sum(c.kcal for c in consumptions_today)
    total_protein = sum(c.protein_g for c in consumptions_today)
    total_carbs = sum(c.carbs_g for c in consumptions_today)
    total_fat = sum(c.fat_g for c in consumptions_today)

    total_macros = total_protein + total_carbs + total_fat
    macro_pct = []
    if total_macros > 0:
        macro_pct.append({"name": "Protein", "value": (total_protein / total_macros) * 100})
        macro_pct.append({"name": "Karbohidrat", "value": (total_carbs / total_macros) * 100})
        macro_pct.append({"name": "Lemak", "value": (total_fat / total_macros) * 100})
    
    # Dummy by_hour data
    by_hour = [{"hour": f"{h:02d}:00", "kcal": (h * 50) % 300} for h in range(24)]

    return schemas.DashboardSummary(
        total_kcal=total_kcal,
        protein_g=total_protein,
        carbs_g=total_carbs,
        fat_g=total_fat,
        macro_pct=macro_pct,
        by_hour=by_hour
    )

# Reports Router
@app.get("/reports", response_model=List[schemas.Report])
def list_reports(range_type: str, start_date: str, end_date: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Implementasi filter laporan
    return crud.get_reports(db, user_id=current_user.id, range_type=range_type, start_date=start_date, end_date=end_date)

@app.post("/reports/generate", response_model=schemas.Report)
def generate_report(report_request: schemas.ReportGenerate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Buat PDF server-side
    pdf_path = pdf_utils.generate_pdf_report(
        user=current_user,
        range_type=report_request.range_type,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
        db=db
    )
    db_report = crud.create_report(
        db,
        user_id=current_user.id,
        range_type=report_request.range_type,
        start_date=report_request.start_date,
        end_date=report_request.end_date,
        pdf_path=pdf_path
    )
    return db_report

# AI Assistant Router
@app.post("/assistant/recommendations")
def get_ai_recommendations(
    ai_request: schemas.AIRecommendationRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ini adalah endpoint yang akan dipanggil oleh frontend AI Assistant
    # Prompt AI Assistant akan dibangun di frontend, dan responsnya akan diproses di sana juga.
    # Backend ini hanya akan meneruskan permintaan ke model AI (jika ada model lokal)
    # atau bisa juga langsung mengembalikan respons dummy jika model AI diakses langsung dari frontend.
    
    # Untuk demo, kita akan mengembalikan respons dummy yang terstruktur
    if ai_request.deficit_calorie > 0:
        recommendations = [
            {"Menu": "Nasi Putih", "Takaran/Porsi": "1.5 porsi sedang (150g)", "Perkiraan_Energi_kkal": 195, "Protein_g": 4, "Karbo_g": 42, "Lemak_g": 0.5},
            {"Menu": "Ayam Bakar/Panggang", "Takaran/Porsi": "1 potong besar (100g)", "Perkiraan_Energi_kkal": 165, "Protein_g": 31, "Karbo_g": 0, "Lemak_g": 5},
            {"Menu": "Sayur Tumis (Kangkung/Bayam)", "Takaran/Porsi": "1 porsi", "Perkiraan_Energi_kkal": 60, "Protein_g": 3, "Karbo_g": 10, "Lemak_g": 2},
        ]
    else:
        recommendations = [
            {"Menu": "Salad Sayur dengan Dada Ayam", "Takaran/Porsi": "1 porsi", "Perkiraan_Energi_kkal": 300, "Protein_g": 25, "Karbo_g": 20, "Lemak_g": 15},
            {"Menu": "Yoghurt Plain", "Takaran/Porsi": "1 cup", "Perkiraan_Energi_kkal": 100, "Protein_g": 10, "Karbo_g": 15, "Lemak_g": 2},
        ]
    
    return {"recommendations": recommendations}


# Jika Anda ingin menjalankan aplikasi secara langsung
if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
def root():
    return {"message": "NIRMAS API is running 🚀"}

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
