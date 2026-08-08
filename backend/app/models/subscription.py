"""
Subscription Database Models
SQLAlchemy ORM models for subscription management
"""

from sqlalchemy import Column, String, Enum, Numeric, Integer, Date, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class BillingCycle(str, enum.Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class InvoiceStatus(str, enum.Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class SubscriptionPlan(Base):
    """Subscription plan model"""
    __tablename__ = "subscription_plans"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Plan Details
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String)
    
    # Pricing
    price_monthly = Column(Numeric(10, 2))
    price_yearly = Column(Numeric(10, 2))
    currency = Column(String(3), default="INR")
    
    # Limits
    max_users = Column(Integer)
    max_issues = Column(Integer)  # Per month
    max_storage_gb = Column(Integer)
    
    # Features (stored as JSON)
    features = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, slug={self.slug})>"


class Subscription(Base):
    """Subscription model - links organization to a plan"""
    __tablename__ = "subscriptions"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription Details
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False, index=True)
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    trial_end_date = Column(Date)
    cancelled_at = Column(DateTime)
    
    # Billing
    amount = Column(Numeric(10, 2))
    currency = Column(String(3), default="INR")
    payment_gateway = Column(String(50))  # 'razorpay', 'stripe', etc.
    payment_gateway_subscription_id = Column(String(255))
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    invoices = relationship("BillingInvoice", back_populates="subscription")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, org_id={self.organization_id}, status={self.status})>"


class BillingInvoice(Base):
    """Billing invoice model"""
    __tablename__ = "billing_invoices"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id"))
    
    # Invoice Details
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR")
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, index=True)
    paid_at = Column(DateTime)
    
    # Payment
    payment_method = Column(String(50))
    payment_gateway_invoice_id = Column(String(255))
    payment_gateway_payment_id = Column(String(255))
    
    # Documents
    invoice_pdf_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    subscription = relationship("Subscription", back_populates="invoices")
    
    def __repr__(self):
        return f"<BillingInvoice(id={self.id}, number={self.invoice_number}, status={self.status})>"


class UsageMetric(Base):
    """Usage metrics model - tracks organization resource usage"""
    __tablename__ = "usage_metrics"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Metrics Period
    metric_date = Column(Date, nullable=False)
    metric_month = Column(String(7), nullable=False)  # 'YYYY-MM' format
    
    # Usage Counters
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    storage_used_gb = Column(Numeric(10, 2), default=0)
    
    # AI Feature Usage (for Phase 2)
    ai_meeting_agendas_generated = Column(Integer, default=0)
    ai_predictions_made = Column(Integer, default=0)
    
    # API Usage
    api_calls = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_metrics")
    
    def __repr__(self):
        return f"<UsageMetric(id={self.id}, org_id={self.organization_id}, date={self.metric_date})>"
