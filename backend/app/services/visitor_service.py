"""
Visitor Service - Business logic for visitor log management
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.visitor import VisitorLog, VisitorStatus
from app.models.user import User, UserRole
from app.schemas.visitor import VisitorLogCreate, VisitorLogUpdate


class VisitorService:

    @staticmethod
    def log_visitor(db: Session, data: VisitorLogCreate, logged_by: str) -> VisitorLog:
        # Prefer the tenant for the unit; fall back to owner/unset if no tenant registered
        host_user = db.query(User).filter(
            User.unit_number == data.host_unit,
            User.role == UserRole.RESIDENT,
            User.is_active == True,
            User.residency_type == 'tenant',
        ).first()
        if not host_user:
            host_user = db.query(User).filter(
                User.unit_number == data.host_unit,
                User.role == UserRole.RESIDENT,
                User.is_active == True,
            ).first()

        visitor = VisitorLog(
            visitor_name=data.visitor_name,
            visitor_phone=data.visitor_phone,
            vehicle_number=data.vehicle_number,
            purpose=data.purpose,
            host_unit=data.host_unit,
            host_user_id=host_user.id if host_user else None,
            logged_by=logged_by,
            notes=data.notes,
            status=VisitorStatus.PENDING,
        )
        db.add(visitor)
        db.commit()
        db.refresh(visitor)
        return visitor

    @staticmethod
    def get_all_visitors(db: Session, skip: int = 0, limit: int = 100) -> List[VisitorLog]:
        return db.query(VisitorLog).order_by(VisitorLog.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_visitor(db: Session, visitor_id: str) -> VisitorLog:
        visitor = db.query(VisitorLog).filter(VisitorLog.id == visitor_id).first()
        if not visitor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor log not found")
        return visitor

    @staticmethod
    def get_visitors_for_resident(db: Session, user_id: str) -> List[VisitorLog]:
        return (
            db.query(VisitorLog)
            .filter(VisitorLog.host_user_id == user_id)
            .order_by(VisitorLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_pending_for_resident(db: Session, user_id: str) -> List[VisitorLog]:
        return (
            db.query(VisitorLog)
            .filter(
                VisitorLog.host_user_id == user_id,
                VisitorLog.status == VisitorStatus.PENDING,
            )
            .order_by(VisitorLog.created_at.desc())
            .all()
        )

    @staticmethod
    def edit_visitor(db: Session, visitor_id: str, data: VisitorLogUpdate, current_user: User) -> VisitorLog:
        visitor = VisitorService.get_visitor(db, visitor_id)
        if visitor.status != VisitorStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending entries can be edited",
            )
        if current_user.role not in (UserRole.SECURITY, UserRole.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Security or Admin access required")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(visitor, field, value)
        # Re-resolve host user if host_unit changed — prefer tenant
        if data.host_unit:
            host_user = db.query(User).filter(
                User.unit_number == visitor.host_unit,
                User.role == UserRole.RESIDENT,
                User.is_active == True,
                User.residency_type == 'tenant',
            ).first()
            if not host_user:
                host_user = db.query(User).filter(
                    User.unit_number == visitor.host_unit,
                    User.role == UserRole.RESIDENT,
                    User.is_active == True,
                ).first()
            visitor.host_user_id = host_user.id if host_user else None
        db.commit()
        db.refresh(visitor)
        return visitor

    @staticmethod
    def update_status(db: Session, visitor_id: str, new_status: VisitorStatus, current_user: User) -> VisitorLog:
        from datetime import datetime

        visitor = VisitorService.get_visitor(db, visitor_id)

        is_security_or_admin = current_user.role in (UserRole.SECURITY, UserRole.ADMIN)
        is_host = visitor.host_user_id == current_user.id

        if new_status in (VisitorStatus.APPROVED, VisitorStatus.DENIED):
            if not is_host and not is_security_or_admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the host or security can approve/deny")
        elif new_status == VisitorStatus.CHECKED_OUT:
            if not is_security_or_admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only security or admin can mark checkout")
            visitor.check_out_time = datetime.utcnow()

        visitor.status = new_status
        db.commit()
        db.refresh(visitor)
        return visitor
