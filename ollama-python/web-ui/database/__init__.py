"""
Database package for AI Dashboard.

This package contains:
- models.py: SQLAlchemy ORM models
- db.py: Database connection and session management
- crud.py: CRUD operations for all models
"""

from database.models import (
    Base,
    User,
    Conversation,
    Message,
    PDF,
    PDFQuery,
    EmailDraft,
    UsageLog
)

from database.db import (
    engine,
    SessionLocal,
    init_db,
    get_db,
    get_db_session
)

__all__ = [
    # Models
    'Base',
    'User',
    'Conversation',
    'Message',
    'PDF',
    'PDFQuery',
    'EmailDraft',
    'UsageLog',
    
    # Database
    'engine',
    'SessionLocal',
    'init_db',
    'get_db',
    'get_db_session',
]
