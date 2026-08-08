"""Water Tanker Management API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, date

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.water_tanker import WaterTankerSupplier, WaterTankerOrder, TankerOrderStatus
from app.schemas.water_tanker import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    OrderCreate, OrderUpdate, OrderResponse,
)

router = APIRouter()


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# ── Supplier endpoints ────────────────────────────────────────────────────────

@router.get("/suppliers", response_model=List[SupplierResponse])
def list_suppliers(
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterTankerSupplier)
    if active_only:
        q = q.filter(WaterTankerSupplier.is_active == True)
    return q.order_by(WaterTankerSupplier.name).all()


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_admin),
):
    supplier = WaterTankerSupplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_admin),
):
    supplier = db.query(WaterTankerSupplier).filter(WaterTankerSupplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(supplier, k, v)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_admin),
):
    supplier = db.query(WaterTankerSupplier).filter(WaterTankerSupplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.is_active = False
    db.commit()


# ── Order endpoints ───────────────────────────────────────────────────────────

@router.get("/orders", response_model=List[OrderResponse])
def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WaterTankerOrder).options(
        joinedload(WaterTankerOrder.supplier),
        joinedload(WaterTankerOrder.creator),
    )
    if status_filter:
        q = q.filter(WaterTankerOrder.status == status_filter)
    if from_date:
        q = q.filter(WaterTankerOrder.scheduled_date >= from_date)
    if to_date:
        q = q.filter(WaterTankerOrder.scheduled_date <= to_date)
    return q.order_by(WaterTankerOrder.scheduled_date.desc()).offset(skip).limit(limit).all()


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = WaterTankerOrder(**data.model_dump(), created_by=current_user.id)
    # auto-calculate amount if supplier has a rate
    if data.supplier_id:
        supplier = db.query(WaterTankerSupplier).filter(
            WaterTankerSupplier.id == data.supplier_id
        ).first()
        if supplier and supplier.rate_per_kl:
            order.amount = float(supplier.rate_per_kl) * float(data.quantity_kl)
    db.add(order)
    db.commit()
    db.refresh(order)
    return db.query(WaterTankerOrder).options(
        joinedload(WaterTankerOrder.supplier),
        joinedload(WaterTankerOrder.creator),
    ).filter(WaterTankerOrder.id == order.id).first()


@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(WaterTankerOrder).filter(WaterTankerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    updates = data.model_dump(exclude_unset=True)
    # stamp delivered_at when status changes to delivered
    if updates.get("status") == "delivered" and not order.delivered_at:
        updates["delivered_at"] = datetime.utcnow()
    for k, v in updates.items():
        setattr(order, k, v)
    db.commit()
    db.refresh(order)
    return db.query(WaterTankerOrder).options(
        joinedload(WaterTankerOrder.supplier),
        joinedload(WaterTankerOrder.creator),
    ).filter(WaterTankerOrder.id == order_id).first()


@router.delete("/orders/{order_id}", status_code=status.HTTP_200_OK)
def cancel_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(WaterTankerOrder).filter(WaterTankerOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == TankerOrderStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Cannot cancel a delivered order")
    order.status = TankerOrderStatus.CANCELLED
    db.commit()
    return {"message": "Order cancelled"}
