"""Налаштування проєкту AI Bird Lab."""

from pathlib import Path

BASE_DIR = Path(file).resolve().parent

DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = BASE_DIR / "samples"
SAMPLES_IMAGES_DIR = SAMPLES_DIR / "images"
SAMPLES_AUDIO_DIR = SAMPLES_DIR / "audio"
OUTPUT_DIR = BASE_DIR / "output"

MODELS_DIR = BASE_DIR / "models"
IMAGE_MODEL_DIR = MODELS_DIR / "bird-image"
AUDIO_MODEL_DIR = MODELS_DIR / "bird-audio"

DB_PATH = DATA_DIR / "birds.db"
BIRDS_INFO_PATH = DATA_DIR / "birds_info.json"
CSV_EXPORT_PATH = OUTPUT_DIR / "bird_analysis.csv"

# Якщо модель уже скачана локально — використовуємо шлях, інакше — ID з HF.
IMAGE_MODEL_ID = (
    str(IMAGE_MODEL_DIR) if IMAGE_MODEL_DIR.exists()
    else "chriamue/bird-species-classifier"
)
AUDIO_MODEL_ID = (
    str(AUDIO_MODEL_DIR) if AUDIO_MODEL_DIR.exists()
    else "DBD-research-group/Bird-MAE-Large"
)
AUDIO_MODEL_TRUST_REMOTE_CODE = True

TOP_K = 3
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}
AUDIO_SAMPLE_RATE = 32_000

for _folder in (DATA_DIR, SAMPLES_IMAGES_DIR, SAMPLES_AUDIO_DIR, OUTPUT_DIR):
    _folder.mkdir(parents=True, exist_ok=True)