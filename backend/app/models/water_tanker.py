"""Water Tanker Management Models"""

from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey, Date, Time, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class TankerOrderStatus(str, enum.Enum):
    SCHEDULED  = "scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"


class WaterTankerSupplier(Base):
    __tablename__ = "water_tanker_suppliers"

    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name         = Column(String, nullable=False)
    contact_name = Column(String)
    phone        = Column(String)
    capacity_kl  = Column(Numeric(8, 2))   # tanker capacity in kilolitres
    rate_per_kl  = Column(Numeric(10, 2))  # price per KL
    is_active    = Column(Boolean, default=True, nullable=False)
    notes        = Column(Text)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, onupdate=func.now())

    orders = relationship("WaterTankerOrder", back_populates="supplier")


class WaterTankerOrder(Base):
    __tablename__ = "water_tanker_orders"

    id                 = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    supplier_id        = Column(String, ForeignKey("water_tanker_suppliers.id", ondelete="SET NULL"), nullable=True)
    scheduled_date     = Column(Date, nullable=False)
    scheduled_time     = Column(Time)
    quantity_kl        = Column(Numeric(8, 2), nullable=False)
    actual_quantity_kl = Column(Numeric(8, 2))
    vehicle_number     = Column(String)   # tanker registration/vehicle number
    driver_name        = Column(String)
    driver_phone       = Column(String)
    departed_time      = Column(Time)     # time tanker left the society
    status             = Column(Enum(TankerOrderStatus), default=TankerOrderStatus.SCHEDULED, nullable=False)
    amount             = Column(Numeric(10, 2), default=0)
    notes              = Column(Text)
    created_by         = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    delivered_at       = Column(DateTime)
    created_at         = Column(DateTime, server_default=func.now())
    updated_at         = Column(DateTime, onupdate=func.now())

    supplier = relationship("WaterTankerSupplier", back_populates="orders")
    creator  = relationship("User", foreign_keys=[created_by])
