"""Water Tanker Management Pydantic Schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date, time
from decimal import Decimal


# ── Supplier Schemas ──────────────────────────────────────────────────────────

class SupplierBase(BaseModel):
    name:         str            = Field(..., min_length=2, max_length=100)
    contact_name: Optional[str]  = None
    phone:        Optional[str]  = None
    capacity_kl:  Optional[Decimal] = Field(None, ge=0, description="Tanker capacity in KL")
    rate_per_kl:  Optional[Decimal] = Field(None, ge=0, description="Rate per KL")
    notes:        Optional[str]  = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name:         Optional[str]     = Field(None, min_length=2, max_length=100)
    contact_name: Optional[str]     = None
    phone:        Optional[str]     = None
    capacity_kl:  Optional[Decimal] = Field(None, ge=0)
    rate_per_kl:  Optional[Decimal] = Field(None, ge=0)
    is_active:    Optional[bool]    = None
    notes:        Optional[str]     = None


class SupplierResponse(SupplierBase):
    id:        str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Order Schemas ─────────────────────────────────────────────────────────────

TankerOrderStatusType = Literal["scheduled", "in_transit", "delivered", "cancelled"]


class OrderBase(BaseModel):
    supplier_id:    Optional[str]    = None
    scheduled_date: date             = Field(..., description="Delivery date")
    scheduled_time: Optional[time]   = Field(None, description="Arrived time")
    departed_time:  Optional[time]   = Field(None, description="Departed time")
    quantity_kl:    Optional[Decimal] = Field(default=Decimal('0'), ge=0, description="Quantity in KL")
    vehicle_number: Optional[str]    = Field(None, max_length=20)
    driver_name:    Optional[str]    = Field(None, max_length=100)
    driver_phone:   Optional[str]    = Field(None, max_length=20)
    notes:          Optional[str]    = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    supplier_id:        Optional[str]            = None
    scheduled_date:     Optional[date]           = None
    scheduled_time:     Optional[time]           = None
    departed_time:      Optional[time]           = None
    quantity_kl:        Optional[Decimal]        = Field(None, ge=0)
    actual_quantity_kl: Optional[Decimal]        = Field(None, ge=0)
    vehicle_number:     Optional[str]            = Field(None, max_length=20)
    driver_name:        Optional[str]            = Field(None, max_length=100)
    driver_phone:       Optional[str]            = Field(None, max_length=20)
    status:             Optional[TankerOrderStatusType] = None
    amount:             Optional[Decimal]        = Field(None, ge=0)
    notes:              Optional[str]            = None


class CreatorSummary(BaseModel):
    id:   str
    name: str

    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    id:                 str
    status:             TankerOrderStatusType
    actual_quantity_kl: Optional[Decimal] = None
    departed_time:      Optional[time]    = None
    amount:             Decimal
    delivered_at:       Optional[datetime] = None
    created_at:         datetime
    supplier:           Optional[SupplierResponse] = None
    creator:            Optional[CreatorSummary]   = None

    @field_validator('status', mode='before')
    @classmethod
    def coerce_status(cls, v):
        return v.value if hasattr(v, 'value') else v

    class Config:
        from_attributes = True
        use_enum_values  = True
