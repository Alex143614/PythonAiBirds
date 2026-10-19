from datetime import datetime

from sqlalchemy import create_engine, select, func, String, Integer, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

import config


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    tablename = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  
    predicted_species: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    analysis_date: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_info: Mapped[str | None] = mapped_column(Text, nullable=True)


engine = create_engine(f"sqlite:///{config.DB_PATH}", echo=False)


def init_db() -> None:
    """Створює таблицю, якщо її немає."""
    Base.metadata.create_all(engine)


def save_analysis(
    file_name: str,
    source_type: str,
    predicted_species: str,
    confidence: float | None,
    description: str | None = None,
    extra_info: str | None = None,
) -> int:
    """Зберігає результат аналізу, повертає id запису."""
    with Session(engine) as session:
        record = Analysis(
            file_name=file_name,
            source_type=source_type,
            predicted_species=predicted_species,
            confidence=confidence,
            analysis_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description=description,
            extra_info=extra_info,
        )
        session.add(record)
        session.commit()
        return record.id


def get_all_analyses() -> list[Analysis]:
    """Повертає всі записи, найновіші першими."""
    with Session(engine) as session:
        stmt = select(Analysis).order_by(Analysis.analysis_date.desc())
        return list(session.scalars(stmt))


def search_by_species(query: str) -> list[Analysis]:
    """Пошук за назвою птаха (часткове співпадіння)."""
    with Session(engine) as session:
        stmt = (
            select(Analysis)
            .where(Analysis.predicted_species.ilike(f"%{query}%"))
            .order_by(Analysis.analysis_date.desc())
        )
        return list(session.scalars(stmt))


def delete_analysis(record_id: int) -> bool:
    """Видаляє запис за id. Повертає True, якщо запис існував."""
    with Session(engine) as session:
        record = session.get(Analysis, record_id)
        if record is None:
            return False
        session.delete(record)
        session.commit()
        return True


def get_statistics() -> dict:
    """Повертає базову статистику."""
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(Analysis))

        most_common = session.execute(
            select(Analysis.predicted_species, func.count().label("cnt"))
            .group_by(Analysis.predicted_species)
            .order_by(func.count().desc())
            .limit(5)
        ).all()

        highest = session.execute(
            select(Analysis.predicted_species, Analysis.confidence)
            .where(Analysis.confidence.is_not(None))
            .order_by(Analysis.confidence.desc())
            .limit(1)
        ).first()

        lowest = session.execute(
            select(Analysis.predicted_species, Analysis.confidence)
            .where(Analysis.confidence.is_not(None))
            .order_by(Analysis.confidence.asc())
            .limit(1)
        ).first()

    return {
        "total": total,
        "most_common": [(row[0], row[1]) for row in most_common],
        "highest_confidence": {"species": highest[0], "confidence": highest[1]} if highest else None,
        "lowest_confidence": {"species": lowest[0], "confidence": lowest[1]} if lowest else None,
    }