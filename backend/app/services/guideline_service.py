from sqlalchemy.orm import Session
from typing import List

from app.models.guideline import SecurityGuideline
from app.schemas.guideline import GuidelineCreate


class GuidelineService:

    @staticmethod
    def get_active(db: Session) -> List[SecurityGuideline]:
        return (
            db.query(SecurityGuideline)
            .filter(SecurityGuideline.is_active == True)
            .order_by(SecurityGuideline.sort_order)
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> List[SecurityGuideline]:
        return db.query(SecurityGuideline).order_by(SecurityGuideline.sort_order).all()

    @staticmethod
    def bulk_replace(db: Session, items: List[GuidelineCreate]) -> List[SecurityGuideline]:
        db.query(SecurityGuideline).delete()
        new_records = [
            SecurityGuideline(**{**item.model_dump(), 'sort_order': i})
            for i, item in enumerate(items)
        ]
        db.add_all(new_records)
        db.commit()
        for r in new_records:
            db.refresh(r)
        return new_records
