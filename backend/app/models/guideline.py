from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class SecurityGuideline(Base):
    __tablename__ = "security_guidelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(500), nullable=False)
    text_hi = Column(String(500), nullable=True)
    # block | check | badge | car | warning
    icon_type = Column(String(20), default="check", nullable=False)
    severity = Column(String(20), default="#e8f5e9", nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
