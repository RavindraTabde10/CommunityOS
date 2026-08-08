"""
Visitor Log Database Model
"""

from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class VisitorStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CHECKED_OUT = "checked_out"


class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    visitor_name = Column(String, nullable=False)
    visitor_phone = Column(String)
    vehicle_number = Column(String)
    purpose = Column(String)
    host_unit = Column(String, nullable=False)
    host_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(VisitorStatus), default=VisitorStatus.PENDING, nullable=False)
    check_in_time = Column(DateTime, server_default=func.now())
    check_out_time = Column(DateTime, nullable=True)
    logged_by = Column(String, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    host = relationship("User", foreign_keys=[host_user_id])
    security_guard = relationship("User", foreign_keys=[logged_by])
