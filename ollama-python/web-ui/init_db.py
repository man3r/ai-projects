#!/usr/bin/env python3
"""
Database initialization script for AI Dashboard.

Run this script once to create the database and all tables:
    python init_db.py
"""

import sys
import os

# Add parent directory to path so we can import database modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, get_db_session
from database.models import User
from database import crud


def main():
    print("=" * 60)
    print("AI Dashboard - Database Initialization")
    print("=" * 60)
    print()
    
    # Initialize database
    init_db()
    print()
    
    # Test database connection
    print("Testing database connection...")
    try:
        db = get_db_session()
        
        # Try to query users table
        user_count = db.query(User).count()
        print(f"✅ Database connection successful!")
        print(f"   Current user count: {user_count}")
        
        db.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    print()
    print("=" * 60)
    print("✅ Database setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start your FastAPI server: uvicorn app:app --reload")
    print("2. Visit http://localhost:8000 and login")
    print("3. Your data will now persist across restarts!")
    print()


if __name__ == "__main__":
    main()
