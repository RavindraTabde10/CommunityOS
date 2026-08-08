"""
Audit Log Database Model
Records sensitive API operations for security monitoring and compliance.
"""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from sqlalchemy.sql import func

from app.db.base import Base


class APIAuditLog(Base):
    """Immutable record of a significant API operation."""

    __tablename__ = "api_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Actor
    user_id = Column(String, nullable=True, index=True)
    user_email = Column(String, nullable=True)

    # Operation
    action = Column(String(100), nullable=False)        # e.g. "login", "delete_issue"
    resource_type = Column(String(50), nullable=True)   # e.g. "issue", "user"
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)               # JSON-encoded extra context

    # Request context
    ip_address = Column(String(45), nullable=True)      # supports IPv6
    user_agent = Column(String(255), nullable=True)
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_api_audit_logs_action", "action"),
        Index("ix_api_audit_logs_created_at", "created_at"),
    )
