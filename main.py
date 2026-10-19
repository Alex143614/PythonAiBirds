"""AI Bird Lab — головний файл застосунку."""

import sys
from pathlib import Path

import config
import database
import exporter
from bird_info import format_bird_info, get_bird_info, load_birds_info


# Моделі завантажуються ліниво — лише коли потрібні,
# щоб запуск меню не чекав на завантаження ваг.
_image_classifier = None
_audio_classifier = None


def get_image_classifier():
    global _image_classifier
    if _image_classifier is None:
        from models import BirdImageClassifier
        print("Завантаження моделі для фото...")
        _image_classifier = BirdImageClassifier()
    return _image_classifier


def get_audio_classifier():
    global _audio_classifier
    if _audio_classifier is None:
        from models import BirdAudioClassifier
        print("Завантаження моделі для аудіо...")
        _audio_classifier = BirdAudioClassifier()
    return _audio_classifier


def _check_extension(path: Path, allowed: set[str]) -> bool:
    return path.suffix.lower() in allowed


def analyze_image() -> None:
    raw = input("Шлях до фото (JPG/JPEG/PNG): ").strip()
    if not raw:
        print("Шлях не вказано.")
        return

    path = Path(raw).expanduser()
    if not path.exists() or not path.is_file():
        print(f"Файл не знайдено: {path}")
        return
    if not _check_extension(path, config.ALLOWED_IMAGE_EXTENSIONS):
        print(f"Непідтримуване розширення: {path.suffix}")
        return

    try:
        classifier = get_image_classifier()
        predictions = classifier.predict(path)
    except Exception as exc:
        print(f"Помилка аналізу зображення: {exc}")
        return

    if not predictions:
        print("Модель не повернула жодного результату.")
        return

    print("\nТоп результатів:")
    for i, item in enumerate(predictions, 1):
        print(f"  {i}. {item['label']} — {item['score']:.2%}")

    best = predictions[0]
    info_result = get_bird_info(best["label"])
    description = info_result["data"].get("fun_facts") if info_result["found"] else None

    record_id = database.save_analysis(
        file_name=path.name,
        source_type="image",
        predicted_species=best["label"],
        confidence=best["score"],
        description=description,
    )
    print(f"\nЗбережено запис №{record_id}.")
    print(format_bird_info(info_result))


def analyze_audio() -> None:
    raw = input("Шлях до аудіо (WAV/FLAC/MP3/OGG/M4A): ").strip()
    if not raw:
        print("Шлях не вказано.")
        return

    path = Path(raw).expanduser()
    if not path.exists() or not path.is_file():
        print(f"Файл не знайдено: {path}")
        return
    if not _check_extension(path, config.ALLOWED_AUDIO_EXTENSIONS):
        print(f"Непідтримуване розширення: {path.suffix}")
        return

    try:
        classifier = get_audio_classifier()
        predictions = classifier.predict(path)
    except Exception as exc:
        print(f"Помилка аналізу аудіо: {exc}")
        return

    if not predictions:
        print("Модель не повернула жодного результату.")
        return

    print("\nПрипущення (аудіоаналіз не є підтвердженим фактом):")
    for i, item in enumerate(predictions, 1):
        print(f"  {i}. {item['label']} — {item['score']:.2%}")

    best = predictions[0]
    info_result = get_bird_info(best["label"])
    description = info_result["data"].get("fun_facts") if info_result["found"] else None

    record_id = database.save_analysis(
        file_name=path.name,
        source_type="audio",
        predicted_species=best["label"],
        confidence=best["score"],
        description=description,
    )
    print(f"\nЗбережено запис №{record_id}.")
    print(format_bird_info(info_result))


def show_history() -> None:
    records = database.get_all_analyses()
    if not records:
        print("Історія порожня.")
        return

    print(f"\nУсього записів: {len(records)}")
    for row in records:
        print(
            f"  [{row.id}] {row.analysis_date} | {row.source_type} | "
            f"{row.predicted_species} | {row.confidence} | {row.file_name}"
        )def search_species() -> None:
    query = input("Назва птаха для пошуку: ").strip()
    if not query:
        print("Порожній запит.")
        return

    results = database.search_by_species(query)
    if not results:
        print("Нічого не знайдено.")
        return

    for row in results:
        print(
            f"  [{row.id}] {row.analysis_date} | {row.predicted_species} "
            f"| {row.confidence} | {row.file_name}"
        )


def delete_record() -> None:
    raw = input("ID запису для видалення: ").strip()
    if not raw.isdigit():
        print("ID має бути числом.")
        return

    if database.delete_analysis(int(raw)):
        print("Запис видалено.")
    else:
        print("Запис із таким ID не знайдено.")


def show_statistics() -> None:
    exporter.print_statistics()


def export_csv() -> None:
    path = exporter.export_to_csv()
    print(f"Експортовано у: {path}")


def show_bird_info() -> None:
    query = input("Введіть назву птаха: ").strip()
    info = load_birds_info()
    print(format_bird_info(get_bird_info(query, info)))


MENU = """
=== AI Bird Lab ===
1. Аналіз фото
2. Аналіз аудіо
3. Історія аналізів
4. Пошук птаха за назвою
5. Видалити запис за ID
6. Показати статистику
7. Експорт у CSV
8. Інформація про птаха
0. Вихід
"""


def main() -> None:
    database.init_db()

    actions = {
        "1": analyze_image,
        "2": analyze_audio,
        "3": show_history,
        "4": search_species,
        "5": delete_record,
        "6": show_statistics,
        "7": export_csv,
        "8": show_bird_info,
    }

    while True:
        print(MENU)
        choice = input("Ваш вибір: ").strip()

        if choice == "0":
            print("До побачення.")
            sys.exit(0)

        action = actions.get(choice)
        if action is None:
            print("Невідома команда.")
            continue

        try:
            action()
        except KeyboardInterrupt:
            print("\nПерервано.")
        except Exception as exc:
            print(f"Непередбачена помилка: {exc}")


if name == "main":
    main()