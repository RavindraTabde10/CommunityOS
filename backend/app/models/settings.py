"""
Organization Settings & Audit Database Models
SQLAlchemy ORM models for settings and audit logs
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class OrganizationSetting(Base):
    """Organization settings model - flexible key-value configuration"""
    __tablename__ = "organization_settings"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Settings
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(JSON, nullable=False)
    setting_type = Column(String(50))  # 'string', 'number', 'boolean', 'json'
    
    # Metadata
    description = Column(String)
    is_system = Column(Boolean, default=False)  # System settings vs. user-configurable
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="settings")
    
    def __repr__(self):
        return f"<OrganizationSetting(id={self.id}, key={self.setting_key})>"


class AuditLog(Base):
    """Audit log model - tracks all important actions"""
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Audit Details
    entity_type = Column(String(50), nullable=False, index=True)  # 'user', 'issue', 'meeting', etc.
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'created', 'updated', 'deleted', 'viewed'
    
    # User Context
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user_email = Column(String(255))
    user_role = Column(String(50))
    
    # Request Context
    ip_address = Column(String(50))
    user_agent = Column(String)
    
    # Changes
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, entity={self.entity_type}, action={self.action})>"
