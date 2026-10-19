"""Обгортки над моделями Hugging Face для аналізу птахів."""

from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification,
    AutoModelForImageClassification,
    AutoProcessor,
)

import config

class BirdImageClassifier:
    """Класифікація виду птаха за фотографією."""

    def init(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.extractor = AutoFeatureExtractor.from_pretrained(config.IMAGE_MODEL_ID)
        self.model = AutoModelForImageClassification.from_pretrained(
            config.IMAGE_MODEL_ID
        ).to(self.device)
        self.model.eval()

    def predict(self, image_path: str | Path, top_k: int = config.TOP_K) -> list[dict]:
        """
        Повертає список словників [{"label": str, "score": float}, ...]
        відсортований за спаданням ймовірності.
        """
        image = Image.open(image_path).convert("RGB")
        inputs = self.extractor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            logits = self.model(**inputs).logits

        probs = torch.softmax(logits, dim=-1)[0]
        top_probs, top_indices = torch.topk(probs, k=min(top_k, probs.shape[-1]))

        results = []
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
            label = self.model.config.id2label.get(idx, f"class_{idx}")
            results.append({"label": label, "score": round(prob, 4)})
        return results

class BirdAudioClassifier:
    """Класифікація птаха за записом співу."""

    def init(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(
            config.AUDIO_MODEL_ID,
            trust_remote_code=config.AUDIO_MODEL_TRUST_REMOTE_CODE,
        )
        self.model = AutoModelForAudioClassification.from_pretrained(
            config.AUDIO_MODEL_ID,
            trust_remote_code=config.AUDIO_MODEL_TRUST_REMOTE_CODE,
        ).to(self.device)
        self.model.eval()

    def predict(self, audio_path: str | Path, top_k: int = config.TOP_K) -> list[dict]:
        """
        Завантажує аудіо, конвертує в моно та цільову частоту,
        повертає топ-k класів.
        """
        import librosa

        waveform, _ = librosa.load(
            str(audio_path),
            sr=config.AUDIO_SAMPLE_RATE,
            mono=True,
        )
        inputs = self.processor(
            waveform,
            sampling_rate=config.AUDIO_SAMPLE_RATE,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits

        probs = torch.softmax(logits, dim=-1)[0]
        top_probs, top_indices = torch.topk(probs, k=min(top_k, probs.shape[-1]))

        results = []
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
            label = self.model.config.id2label.get(idx, f"class_{idx}")
            results.append({"label": label, "score": round(prob, 4)})
        return results