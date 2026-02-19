# Database Setup Instructions

## 📦 Files Included

```
database/
├── __init__.py         # Package initialization
├── models.py           # SQLAlchemy models (7 tables)
├── db.py              # Database connection
├── crud.py            # CRUD operations
└── init_db.py         # Initialization script
```

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd ~/ollama-python/web-ui
pip3 install sqlalchemy --break-system-packages
```

### Step 2: Create Database Folder
```bash
mkdir database
```

### Step 3: Copy Files
Copy all 5 files into the `database/` folder:
- `__init__.py`
- `models.py`
- `db.py`
- `crud.py`
- `init_db.py` (place this in web-ui root, not inside database/)

Your structure should look like:
```
web-ui/
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── db.py
│   └── crud.py
├── init_db.py          ← Note: root level
├── app.py
├── templates/
└── ...
```

### Step 4: Initialize Database
```bash
python3 init_db.py
```

You should see:
```
============================================================
AI Dashboard - Database Initialization
============================================================

Creating database tables...
✅ Database tables created successfully!
✅ SQLite WAL mode enabled

Testing database connection...
✅ Database connection successful!
   Current user count: 0

============================================================
✅ Database setup complete!
============================================================
```

This creates `ai_dashboard.db` in your web-ui folder.

### Step 5: Test It Works
```python
from database.db import get_db_session
from database import crud

# Get a database session
db = get_db_session()

# Create a test user
user = crud.get_or_create_user(
    db,
    email="test@example.com",
    name="Test User"
)

print(f"Created user: {user.email}")

# Clean up
db.close()
```

---

## 📊 Database Schema

### Tables Created:
1. **users** - User accounts
2. **conversations** - Chat conversations
3. **messages** - Individual messages
4. **pdfs** - Uploaded PDF files
5. **pdf_queries** - PDF Q&A history
6. **email_drafts** - Saved email drafts
7. **usage_logs** - Analytics/usage tracking

---

## 🔧 Using in Your App

### Example 1: Save Chat Message
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database import crud

@app.post("/api/chat")
async def chat(
    message: str,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    # Save user message
    crud.add_message(
        db=db,
        conversation_id=conversation_id,
        role="user",
        content=message
    )
    
    # Get AI response...
    ai_response = "..."
    
    # Save AI message
    crud.add_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )
    
    return {"response": ai_response}
```

### Example 2: Get User Conversations
```python
@app.get("/api/conversations")
async def get_conversations(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    conversations = crud.get_user_conversations(
        db=db,
        user_id=user_record.id,
        limit=20
    )
    
    return {"conversations": conversations}
```

### Example 3: Save PDF Record
```python
@app.post("/api/pdf/upload")
async def upload_pdf(
    file: UploadFile,
    db: Session = Depends(get_db)
):
    # ... process PDF ...
    
    pdf_record = crud.create_pdf_record(
        db=db,
        user_id=user.id,
        filename="stored_filename.pdf",
        original_filename=file.filename,
        file_size=file_size,
        page_count=num_pages,
        chunk_count=num_chunks,
        collection_name="user_1_pdf_123"
    )
    
    return {"pdf_id": pdf_record.id}
```

---

## 🗄️ Database File Location

The SQLite database is created at:
```
~/ollama-python/web-ui/ai_dashboard.db
```

### Backup Your Database
```bash
# Simple backup
cp ai_dashboard.db ai_dashboard_backup.db

# Or use SQLite backup command
sqlite3 ai_dashboard.db ".backup ai_dashboard_backup.db"
```

### View Database Contents
```bash
# Install SQLite browser (optional)
brew install --cask db-browser-for-sqlite

# Or use command line
sqlite3 ai_dashboard.db
> .tables
> SELECT * FROM users;
> .quit
```

---

## 🐛 Troubleshooting

### "No module named 'database'"
Make sure you're running from the `web-ui` directory:
```bash
cd ~/ollama-python/web-ui
python3 init_db.py
```

### "Database is locked"
Someone else is accessing the database. Close all connections:
```bash
# Find processes using the database
lsof ai_dashboard.db

# Kill them if needed
pkill -f uvicorn
```

### Start Fresh
```bash
# Delete database and recreate
rm ai_dashboard.db
python3 init_db.py
```

---

## 📚 Available CRUD Functions

Check `crud.py` for all available functions:

**Users:**
- `get_or_create_user()`
- `get_user_by_email()`
- `get_user_by_id()`

**Conversations:**
- `create_conversation()`
- `get_user_conversations()`
- `search_conversations()`
- `delete_conversation()`

**Messages:**
- `add_message()`
- `get_conversation_messages()`

**PDFs:**
- `create_pdf_record()`
- `get_user_pdfs()`
- `get_pdf_by_id()`
- `delete_pdf()`
- `add_pdf_query()`

**Email Drafts:**
- `create_email_draft()`
- `get_user_drafts()`
- `get_email_templates()`

**Usage Logs:**
- `log_usage()`
- `get_user_usage_stats()`

---

## ✅ Next Steps

After database setup, you'll want to:

1. **Update your app.py** to use the database
2. **Add chat history UI** to show past conversations
3. **Implement multi-PDF support** using the pdfs table
4. **Add error logging** using usage_logs

See the detailed Priority 1 guide for implementation examples!

---

## 💡 Tips

- The database uses **WAL mode** for better concurrent access
- All tables have **proper indexes** for fast queries
- Relationships use **CASCADE DELETE** so deleting a user deletes all their data
- The `get_db()` function is a FastAPI dependency - use it in routes
- The `get_db_session()` function is for standalone scripts

---

**Questions?** Check the detailed implementation guide or ask for help! 🚀
