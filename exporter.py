"""Експорт результатів аналізу в CSV та зведена статистика."""

import csv

import config
import database


CSV_FIELDS = [
    "image_name",
    "predicted_species",
    "confidence",
    "analysis_date",
    "description",
]


def export_to_csv(output_path: str | None = None) -> str:
    """
    Експортує всі записи з БД у CSV.
    Повертає шлях до створеного файлу.
    """
    path = output_path or str(config.CSV_EXPORT_PATH)
    records = database.get_all_analyses()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in records:
            writer.writerow({
                "image_name": row.file_name,
                "predicted_species": row.predicted_species,
                "confidence": row.confidence if row.confidence is not None else "",
                "analysis_date": row.analysis_date,
                "description": row.description or "",
            })

    return path


def print_statistics() -> None:
    """Друкує зведену статистику в консоль."""
    stats = database.get_statistics()

    print("\n=== Статистика аналізів ===")
    print(f"Усього записів: {stats['total']}")

    if stats["most_common"]:
        print("Найчастіші види:")
        for species, count in stats["most_common"]:
            print(f"  - {species}: {count}")

    high = stats["highest_confidence"]
    low = stats["lowest_confidence"]

    if high:
        print(f"Найвища впевненість: {high['species']} ({high['confidence']})")
    if low:
        print(f"Найнижча впевненість: {low['species']} ({low['confidence']})")

    print("============================\n")