"""
Database Base Configuration
All models should import from this file
"""
from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base
Base = declarative_base()

# Note: Models are imported in alembic/env.py for migrations
# Do not import models here to avoid circular imports
