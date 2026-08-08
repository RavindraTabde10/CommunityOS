"""
Audit Service
Records security-relevant operations to the audit_logs table.
"""
import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import APIAuditLog

logger = logging.getLogger("api.audit")


class AuditService:
    """Writes and queries audit log entries."""

    @staticmethod
    def log(
        db: Session,
        action: str,
        *,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        http_method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """Persist an audit log entry. Failures are logged but never bubble up."""
        try:
            entry = APIAuditLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                http_method=http_method,
                endpoint=endpoint,
                status_code=status_code,
            )
            db.add(entry)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Failed to write audit log [action=%s]: %s", action, exc)

    @staticmethod
    def get_logs(
        db: Session,
        *,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[APIAuditLog]:
        """Return audit entries filtered by optional user and/or action."""
        query = db.query(APIAuditLog)
        if user_id:
            query = query.filter(APIAuditLog.user_id == user_id)
        if action:
            query = query.filter(APIAuditLog.action == action)
        return (
            query.order_by(APIAuditLog.created_at.desc()).offset(skip).limit(limit).all()
        )
