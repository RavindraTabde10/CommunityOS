"""
Visitor Log Pydantic Schemas
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class VisitorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CHECKED_OUT = "checked_out"


class VisitorLogCreate(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=100)
    visitor_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    purpose: Optional[str] = None
    host_unit: str = Field(..., min_length=1)
    notes: Optional[str] = None


class VisitorStatusUpdate(BaseModel):
    status: VisitorStatus


class VisitorLogUpdate(BaseModel):
    visitor_name: Optional[str] = Field(None, min_length=1, max_length=100)
    visitor_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    purpose: Optional[str] = None
    host_unit: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None


class VisitorLogResponse(BaseModel):
    id: str
    visitor_name: str
    visitor_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    purpose: Optional[str] = None
    host_unit: str
    host_user_id: Optional[str] = None
    host_name: Optional[str] = None
    host_phone: Optional[str] = None
    status: VisitorStatus
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    logged_by: str
    notes: Optional[str] = None
    created_at: datetime

    @model_validator(mode='before')
    @classmethod
    def populate_host_info(cls, data):
        # Populate host_name and host_phone from the ORM relationship
        if hasattr(data, 'host') and data.host:
            data.__dict__.setdefault('host_name', data.host.name)
            data.__dict__.setdefault('host_phone', data.host.phone)
        return data

    class Config:
        from_attributes = True
