import json
from pathlib import Path

import config


# Поля, які очікуються в довіднику для кожного птаха.
EXPECTED_FIELDS = (
    "ukrainian_name",
    "scientific_name",
    "family",
    "habitat",
    "distribution",
    "diet",
    "size",
    "fun_facts",
    "conservation_status",
)


def load_birds_info(path: str | Path | None = None) -> dict:
    """
    Завантажує JSON-довідник птахів.
    Повертає словник виду { "Назва виду": { ...поля... }, ... }.
    Якщо файл відсутній або пошкоджений — повертає порожній словник.
    """
    path = Path(path) if path else config.BIRDS_INFO_PATH

    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def get_bird_info(species_name: str, info: dict | None = None) -> dict:
    """
    Повертає інформацію про птаха за назвою.
    Пошук регістронезалежний, з підтримкою часткового співпадіння.
    Якщо нічого не знайдено — повертає словник із позначкою found=False.
    """
    if info is None:
        info = load_birds_info()

    if not info or not species_name:
        return {"found": False, "species": species_name}

    target = species_name.strip().lower()

    # 1. Точний збіг (без урахування регістру)
    for key, value in info.items():
        if key.strip().lower() == target:
            return {"found": True, "species": key, "data": value}

    # 2. Часткове співпадіння (наприклад, модель повернула "European Robin",
    #    а в довіднику ключ "European Robin (Erithacus rubecula)")
    for key, value in info.items():
        if target in key.lower() or key.lower() in target:
            return {"found": True, "species": key, "data": value}

    return {"found": False, "species": species_name}


def format_bird_info(result: dict) -> str:
    """
    Форматує результат get_bird_info у читабельний текст для консолі.
    Якщо даних немає — повідомляє про це явно.
    """
    if not result.get("found"):
        return f"Інформацію про вид '{result.get('species', '')}' не знайдено в довіднику."

    data = result.get("data", {})
    lines = [f"Вид: {result['species']}"]

    mapping = {
        "ukrainian_name": "Українська назва",
        "scientific_name": "Наукова назва",
        "family": "Родина",
        "habitat": "Середовище існування",
        "distribution": "Географічне поширення",
        "diet": "Тип живлення",
        "size": "Середні розміри",
        "fun_facts": "Цікаві факти",
        "conservation_status": "Природоохоронний статус",
    }

    for field, label in mapping.items():
        value = data.get(field)
        if value:
            lines.append(f"  {label}: {value}")

    return "\n".join(lines)