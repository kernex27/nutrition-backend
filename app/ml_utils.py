# app/ml_utils.py
from typing import List, Dict, Any, Optional
import numpy as np

# Fungsi utilitas Beer-Lambert
def beer_lambert_law(absorbance: float, molar_absorptivity: float, path_length_cm: float) -> float:
    """
    Menghitung konsentrasi berdasarkan Hukum Beer-Lambert.
    A = ε * c * l
    c = A / (ε * l)

    Args:
        absorbance (float): Absorbansi spektrum pada panjang gelombang tertentu.
        molar_absorptivity (float): Koefisien absorptivitas molar (ε).
        path_length_cm (float): Panjang jalur optik (l) dalam cm.

    Returns:
        float: Konsentrasi (c).
    """
    if molar_absorptivity == 0 or path_length_cm == 0:
        return 0.0 # Hindari pembagian dengan nol
    return absorbance / (molar_absorptivity * path_length_cm)

# Fungsi untuk ekstraksi fitur dari spektrum (placeholder)
def extract_features_from_spectra(wavelengths: List[float], absorbance: List[float]) -> Dict[str, Any]:
    """
    Mengekstrak fitur-fitur relevan dari data spektrum.
    Ini adalah implementasi dummy; dalam kasus nyata akan melibatkan algoritma ML.
    """
    features = {}
    if not wavelengths or not absorbance:
        return features

    # Contoh fitur dummy: rata-rata absorbansi, puncak max, dll.
    features["mean_absorbance"] = np.mean(absorbance)
    features["max_absorbance"] = np.max(absorbance)
    features["min_absorbance"] = np.min(absorbance)
    features["std_absorbance"] = np.std(absorbance)
    
    # Placeholder untuk fitur turunan atau area band tertentu
    # Misalnya, mencari puncak di rentang panjang gelombang tertentu
    if len(wavelengths) > 1:
        diff_absorbance = np.diff(absorbance).tolist()
        features["mean_diff_absorbance"] = np.mean(diff_absorbance)
        # Anda bisa menambahkan logika untuk mendeteksi puncak, area di bawah kurva, dll.

    return features

# Fungsi untuk simulasi prediksi ML
def simulate_ml_prediction(
    wavelengths: List[float],
    absorbance: List[float],
    path_length_cm: float,
    molar_absorptivity: Optional[float] = None,
    model_features: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Simulasi prediksi nutrisi (kcal, protein, carbs, fat) dari data spektrum.
    Dalam aplikasi nyata, ini akan memuat model ML yang sudah dilatih (misal: PLS, NN)
    dan menggunakannya untuk memprediksi nilai.
    """
    # Ekstraksi fitur (bisa menggunakan model_features yang disediakan jika ada)
    features = model_features if model_features else extract_features_from_spectra(wavelengths, absorbance)

    # Contoh logika prediksi dummy berdasarkan fitur
    # Ini sangat disederhanakan; model ML sungguhan akan jauh lebih kompleks
    predicted_kcal = 1000 + (features.get("mean_absorbance", 0) * 500) + (features.get("max_absorbance", 0) * 200)
    predicted_protein = 50 + (features.get("mean_absorbance", 0) * 10)
    predicted_carbs = 150 + (features.get("mean_absorbance", 0) * 20)
    predicted_fat = 30 + (features.get("mean_absorbance", 0) * 5)

    # Pastikan nilai tidak negatif
    predicted_kcal = max(0, predicted_kcal)
    predicted_protein = max(0, predicted_protein)
    predicted_carbs = max(0, predicted_carbs)
    predicted_fat = max(0, predicted_fat)

    return {
        "predicted_kcal": round(predicted_kcal, 2),
        "protein_g": round(predicted_protein, 2),
        "carbs_g": round(predicted_carbs, 2),
        "fat_g": round(predicted_fat, 2),
        "model_version": "v1.0-simulated",
        "quality_score": np.random.rand() * 0.2 + 0.7 # Skor kualitas dummy antara 0.7 dan 0.9
    }

