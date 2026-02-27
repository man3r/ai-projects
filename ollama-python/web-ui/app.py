from pydantic import BaseModel
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import ollama
import chromadb
import pypdf
import os
import json
from dotenv import load_dotenv
from auth import oauth, get_current_user
from database.db import get_db, init_db
from database import crud
from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List  # ← Make sure this is here
from pydantic import BaseModel


import json
import os
# ... rest of your imports

# Store CRUD imports
from database.crud_store import (
    get_business_by_user, 
    get_business_by_slug,
    create_business,
    list_categories, 
    create_category,
    list_products, 
    get_product, 
    create_product, 
    update_product, 
    search_products,
    get_or_create_customer, 
    create_order,
    list_orders, 
    get_order, 
    get_order_by_number, 
    update_order_status,
    get_today_orders, 
    get_order_stats, 
    get_popular_products
)


# ═══════════════════════════════════════════════════════════════════
# PYDANTIC MODELS (Request Validation)
# ═══════════════════════════════════════════════════════════════════

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: float
    unit: Optional[str] = None
    in_stock: bool = True
    is_featured: bool = False

class OrderCreate(BaseModel):
    items: List[dict]  # [{"product_id": 1, "quantity": 2}]
    customer_phone: str
    customer_name: Optional[str] = None
    delivery_address: dict
    customer_notes: Optional[str] = None
    delivery_instructions: Optional[str] = None

# AI helpers
from utils.ai_helpers import (
    chat_with_customer, generate_product_description,
    suggest_complementary_products, parse_order_from_text
)

# Demo data
from utils.demo_data import create_demo_store

load_dotenv()

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

app = FastAPI(title="Local AI Dashboard")

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SECRET_KEY')
)

templates = Jinja2Templates(directory="templates")

# ChromaDB setup
chroma_client = chromadb.Client()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized and ready")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    print("✅ Uploads directory ready")


# ─── Auth Routes ──────────────────────────────────────

@app.get("/login")
async def login(request: Request):
    """Initiates Google OAuth flow"""
    redirect_uri = str(request.url_for('auth_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handles OAuth callback from Google"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = {
                'email': user['email'],
                'name': user.get('name', user['email']),
                'picture': user.get('picture', '')
            }
        return RedirectResponse(url='/', status_code=302)
    except Exception as e:
        print(f"Auth error: {e}")
        return RedirectResponse(url='/login-page', status_code=302)


@app.get("/logout")
async def logout(request: Request):
    """Clears session and redirects to login"""
    request.session.clear()
    return RedirectResponse(url='/login-page', status_code=302)


# ─── Login Page ───────────────────────────────────────

@app.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    """Shows the login page"""
    return templates.TemplateResponse("login.html", {"request": request})


# ─── Main Dashboard ───────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard - requires authentication"""
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login-page', status_code=302)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })


# ─── Ollama Models ───────────────────────────────────────

@app.get("/api/models")
async def list_models():
    """List available Ollama models"""
    try:
        response = ollama.list()
        model_list = getattr(response, "models", []) or []
        models = [getattr(m, "model", getattr(m, "name", str(m))) for m in model_list if m]
        return {"models": models if models else [DEFAULT_MODEL], "default": DEFAULT_MODEL}
    except Exception as e:
        return {"models": [DEFAULT_MODEL], "default": DEFAULT_MODEL, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# CHATBOT WITH DATABASE
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/chat")
async def chat(
    request: Request,
    message: str = Form(...),
    conversation_id: int = Form(None),
    model: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Chat endpoint with database persistence.
    - Creates or continues conversations
    - Saves all messages to database
    - Returns conversation_id for tracking
    """
    user = get_current_user(request)
    user_record = crud.get_or_create_user(
        db, 
        email=user['email'], 
        name=user.get('name'),
        picture_url=user.get('picture')
    )
    
    # Get or create conversation
    if conversation_id:
        conversation = crud.get_conversation(db, conversation_id, user_record.id)
        if not conversation:
            # Invalid conversation_id, create new one
            conversation = crud.create_conversation(db, user_record.id)
    else:
        # New conversation
        conversation = crud.create_conversation(db, user_record.id)
    
    # Save user message to database
    crud.add_message(db, conversation.id, "user", message)
    
    # Get full conversation history from database
    messages = crud.get_conversation_messages(db, conversation.id)
    chat_history = [{"role": msg.role, "content": msg.content} for msg in messages]
    
    chat_model = model or DEFAULT_MODEL
    def stream():
        full_response = ""
        try:
            for chunk in ollama.chat(
                model=chat_model,
                messages=chat_history,
                stream=True
            ):
                content = chunk["message"]["content"]
                full_response += content
                # Send both content and conversation_id
                yield f"data: {json.dumps({'content': content, 'conversation_id': conversation.id})}\n\n"
            
            # Save assistant message to database
            crud.add_message(db, conversation.id, "assistant", full_response)
            
            # Log usage
            crud.log_usage(
                db, 
                user_record.id, 
                tool="chat", 
                action="message_sent",
                extra_data={"conversation_id": conversation.id, "message_length": len(message)}
            )
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/conversations")
async def get_conversations(request: Request, db: Session = Depends(get_db)):
    """Get all conversations for the logged-in user"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    conversations = crud.get_user_conversations(db, user_record.id, limit=50)
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title or "New Conversation",
                "message_count": conv.message_count,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    }


@app.get("/api/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    conversation = crud.get_conversation(db, conversation_id, user_record.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = crud.get_conversation_messages(db, conversation_id)
    
    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.title or "New Conversation",
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "message_count": conversation.message_count
        },
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    success = crud.delete_conversation(db, conversation_id, user_record.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "deleted"}


@app.get("/api/conversations/search")
async def search_conversations_endpoint(
    q: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Search conversations"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    conversations = crud.search_conversations(db, user_record.id, q, limit=10)
    
    return {
        "results": [
            {
                "id": conv.id,
                "title": conv.title or "New Conversation",
                "message_count": conv.message_count,
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    }


# ═══════════════════════════════════════════════════════════════════
# EMAIL WRITER WITH DATABASE
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/email")
async def write_email(
    request: Request,
    description: str = Form(...),
    tone: str = Form("professional"),
    save_draft: str = Form("false"),
    model: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Generate email with optional draft saving.
    """
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    prompt = f"""Write a {tone} email based on this description:
{description}

Format the output as:
Subject: <subject line>

<email body>

Keep it concise and clear."""

    email_model = model or DEFAULT_MODEL
    def stream():
        full_response = ""
        subject = ""
        body = ""
        
        try:
            for chunk in ollama.chat(
                model=email_model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            ):
                content = chunk["message"]["content"]
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Parse subject and body from response
            if "Subject:" in full_response:
                parts = full_response.split("\n", 2)
                if len(parts) >= 2:
                    subject = parts[0].replace("Subject:", "").strip()
                    body = parts[2].strip() if len(parts) > 2 else parts[1].strip()
                else:
                    body = full_response
            else:
                body = full_response
            
            # Save draft if requested
            if str(save_draft).lower() == "true":
                crud.create_email_draft(
                    db,
                    user_id=user_record.id,
                    description=description,
                    tone=tone,
                    subject=subject,
                    body=body
                )
            
            # Log usage
            crud.log_usage(
                db,
                user_record.id,
                tool="email",
                action="email_generated",
                extra_data={"tone": tone, "saved": str(save_draft).lower() == "true"}
            )
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/email/drafts")
async def get_email_drafts(request: Request, db: Session = Depends(get_db)):
    """Get saved email drafts"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    drafts = crud.get_user_drafts(db, user_record.id, limit=20)
    
    return {
        "drafts": [
            {
                "id": draft.id,
                "subject": draft.subject,
                "tone": draft.tone,
                "description": draft.description,
                "created_at": draft.created_at.isoformat()
            }
            for draft in drafts
        ]
    }


@app.get("/api/email/drafts/{draft_id}")
async def get_email_draft_detail(
    draft_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific email draft"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    draft = db.query(crud.EmailDraft)\
        .filter(crud.EmailDraft.id == draft_id, crud.EmailDraft.user_id == user_record.id)\
        .first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    return {
        "id": draft.id,
        "subject": draft.subject,
        "body": draft.body,
        "tone": draft.tone,
        "description": draft.description,
        "created_at": draft.created_at.isoformat()
    }


# ═══════════════════════════════════════════════════════════════════
# PDF CHAT WITH DATABASE (MULTI-PDF SUPPORT)
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/pdf/upload")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process PDF with database tracking.
    Each PDF gets its own ChromaDB collection.
    """
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    # Generate unique filename and collection name
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"user_{user_record.id}_pdf_{timestamp}_{file.filename}"
    filepath = f"uploads/{safe_filename}"
    collection_name = f"user_{user_record.id}_pdf_{timestamp}"
    
    # Save file
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
        file_size = len(content)
    
    # Extract text and create chunks
    reader = pypdf.PdfReader(filepath)
    chunks = []
    
    for page in reader.pages:
        text = page.extract_text()
        if text.strip():
            words = text.split()
            chunk = ""
            for word in words:
                chunk += word + " "
                if len(chunk) >= 500:
                    chunks.append(chunk.strip())
                    chunk = ""
            if chunk:
                chunks.append(chunk.strip())
    
    # Create ChromaDB collection for this PDF
    try:
        pdf_collection = chroma_client.create_collection(collection_name)
    except Exception:
        # Collection might already exist, get it
        pdf_collection = chroma_client.get_collection(collection_name)
    
    # Store embeddings (use embedding model; fallback to default if needed)
    embed_model = EMBEDDING_MODEL
    for i, chunk in enumerate(chunks):
        try:
            response = ollama.embeddings(model=embed_model, prompt=chunk)
        except Exception:
            response = ollama.embeddings(model=DEFAULT_MODEL, prompt=chunk)
        pdf_collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[response["embedding"]],
            documents=[chunk]
        )
    
    # Save PDF record to database
    pdf_record = crud.create_pdf_record(
        db,
        user_id=user_record.id,
        filename=safe_filename,
        original_filename=file.filename,
        file_size=file_size,
        page_count=len(reader.pages),
        chunk_count=len(chunks),
        collection_name=collection_name
    )
    
    # Log usage
    crud.log_usage(
        db,
        user_record.id,
        tool="pdf",
        action="pdf_uploaded",
        extra_data={"filename": file.filename, "pages": len(reader.pages), "chunks": len(chunks)}
    )
    
    return {
        "status": "success",
        "pdf_id": pdf_record.id,
        "filename": file.filename,
        "chunks": len(chunks),
        "pages": len(reader.pages)
    }


@app.get("/api/pdfs")
async def get_user_pdfs(request: Request, db: Session = Depends(get_db)):
    """Get all PDFs for the logged-in user"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    pdfs = crud.get_user_pdfs(db, user_record.id)
    
    return {
        "pdfs": [
            {
                "id": pdf.id,
                "filename": pdf.original_filename,
                "page_count": pdf.page_count,
                "chunk_count": pdf.chunk_count,
                "uploaded_at": pdf.uploaded_at.isoformat(),
                "status": pdf.status
            }
            for pdf in pdfs
        ]
    }


@app.post("/api/pdf/ask")
async def ask_pdf(
    request: Request,
    question: str = Form(...),
    pdf_id: int = Form(...),
    model: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ask a question about a specific PDF.
    Requires pdf_id to know which PDF to query.
    """
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    # Get PDF record
    pdf = crud.get_pdf_by_id(db, pdf_id, user_record.id)
    if not pdf:
        return {"error": "PDF not found or you don't have access to it"}
    
    # Update last accessed time
    crud.update_pdf_access(db, pdf_id, user_record.id)
    
    # Get the ChromaDB collection for this PDF
    try:
        pdf_collection = chroma_client.get_collection(pdf.collection_name)
    except Exception:
        return {"error": "PDF collection not found. Please re-upload the PDF."}
    
    # Generate question embedding
    try:
        question_embedding = ollama.embeddings(model=EMBEDDING_MODEL, prompt=question)
    except Exception:
        question_embedding = ollama.embeddings(model=DEFAULT_MODEL, prompt=question)
    
    # Search for relevant chunks
    results = pdf_collection.query(
        query_embeddings=[question_embedding["embedding"]],
        n_results=3
    )
    
    context = "\n\n".join(results["documents"][0])
    
    prompt = f"""Use the following context from the PDF document "{pdf.original_filename}" to answer the question.
Only use information from the context. If the answer is not in the context, say so.

Context:
{context}

Question: {question}

Answer:"""

    pdf_model = model or DEFAULT_MODEL
    def stream():
        full_response = ""
        try:
            for chunk in ollama.chat(
                model=pdf_model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            ):
                content = chunk["message"]["content"]
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Save query to database
            crud.add_pdf_query(
                db,
                pdf_id=pdf_id,
                user_id=user_record.id,
                question=question,
                answer=full_response
            )
            
            # Log usage
            crud.log_usage(
                db,
                user_record.id,
                tool="pdf",
                action="pdf_query",
                extra_data={"pdf_id": pdf_id, "question_length": len(question)}
            )
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/pdf/{pdf_id}/history")
async def get_pdf_history(
    pdf_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get query history for a specific PDF"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    queries = crud.get_pdf_queries(db, pdf_id, user_record.id, limit=20)
    
    return {
        "queries": [
            {
                "id": q.id,
                "question": q.question,
                "answer": q.answer,
                "created_at": q.created_at.isoformat()
            }
            for q in queries
        ]
    }


@app.delete("/api/pdf/{pdf_id}")
async def delete_pdf_endpoint(
    pdf_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a PDF and its ChromaDB collection"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    # Get PDF record
    pdf = crud.get_pdf_by_id(db, pdf_id, user_record.id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Delete ChromaDB collection
    try:
        chroma_client.delete_collection(pdf.collection_name)
    except Exception as e:
        print(f"Warning: Could not delete ChromaDB collection: {e}")
    
    # Delete file
    try:
        os.remove(f"uploads/{pdf.filename}")
    except Exception as e:
        print(f"Warning: Could not delete file: {e}")
    
    # Delete from database
    success = crud.delete_pdf(db, pdf_id, user_record.id)
    if not success:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return {"status": "deleted"}


# ═══════════════════════════════════════════════════════════════════
# ANALYTICS / STATS
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/stats")
async def get_user_stats(request: Request, db: Session = Depends(get_db)):
    """Get usage statistics for the current user"""
    user = get_current_user(request)
    user_record = crud.get_or_create_user(db, user['email'])
    
    stats = crud.get_user_usage_stats(db, user_record.id, days=30)
    
    # Add conversation and PDF counts
    conversation_count = len(crud.get_user_conversations(db, user_record.id))
    pdf_count = len(crud.get_user_pdfs(db, user_record.id))
    
    return {
        "conversations": conversation_count,
        "pdfs": pdf_count,
        "usage": stats
    }

# ═══════════════════════════════════════════════════════════════════
# ADMIN ROUTES (Business Owner)
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/store/dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Get dashboard overview stats"""
    user = get_current_user(request)
    
    # Get business for this user
    business = get_business_by_user(db, user['id'])
    
    if not business:
        return JSONResponse({
            "status": "no_business",
            "message": "No business setup yet"
        })
    
    # Get today's stats
    today_orders = get_today_orders(db, business.id)
    stats = get_order_stats(db, business.id, days=7)
    popular = get_popular_products(db, business.id, limit=5)
    
    # Count orders by status
    pending = [o for o in today_orders if o.status == 'pending']
    preparing = [o for o in today_orders if o.status == 'preparing']
    ready = [o for o in today_orders if o.status == 'ready']
    
    return {
        "business": {
            "name": business.name,
            "slug": business.slug,
            "is_open": business.is_open,
            "total_orders": business.total_orders,
            "total_revenue": business.total_revenue
        },
        "today": {
            "orders": len(today_orders),
            "revenue": sum(o.total for o in today_orders if o.status == 'delivered'),
            "pending": len(pending),
            "preparing": len(preparing),
            "ready": len(ready)
        },
        "week": stats,
        "popular_products": [
            {"name": p[1], "times_ordered": p[2], "revenue": p[3]}
            for p in popular
        ]
    }


@app.get("/api/store/products")
async def admin_list_products(
    request: Request,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all products for business owner"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    products = list_products(
        db,
        business.id,
        category_id=category_id,
        active_only=False  # Show all for admin
    )
    
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "unit": p.unit,
                "category_id": p.category_id,
                "in_stock": p.in_stock,
                "stock_quantity": p.stock_quantity,
                "is_active": p.is_active,
                "is_featured": p.is_featured,
                "times_ordered": p.times_ordered,
                "image_url": p.image_url
            }
            for p in products
        ]
    }


@app.post("/api/store/products")
async def admin_create_product(
    request: Request,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create new product"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    new_product = create_product(
        db,
        business_id=business.id,
        name=product.name,
        description=product.description,
        price=product.price,
        unit=product.unit,
        category_id=product.category_id,
        in_stock=product.in_stock,
        is_featured=product.is_featured
    )
    
    return {"status": "success", "product_id": new_product.id}


@app.put("/api/store/products/{product_id}")
async def admin_update_product(
    request: Request,
    product_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update product"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    product = get_product(db, product_id)
    if not product or product.business_id != business.id:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated = update_product(db, product_id, **updates)
    
    return {"status": "success", "product": {"id": updated.id, "name": updated.name}}


@app.post("/api/store/products/ai-describe")
async def ai_generate_description(
    request: Request,
    product_name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    unit: str = Form(None)
):
    """AI-generate product description"""
    description = await generate_product_description(product_name, category, price, unit)
    return {"description": description}


@app.get("/api/store/categories")
async def admin_list_categories(request: Request, db: Session = Depends(get_db)):
    """List all categories"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    categories = list_categories(db, business.id, active_only=False)
    
    return {
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "icon": c.icon,
                "display_order": c.display_order,
                "is_active": c.is_active,
                "product_count": len(c.products)
            }
            for c in categories
        ]
    }


@app.get("/api/store/orders")
async def admin_list_orders(
    request: Request,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List orders for business owner"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    orders = list_orders(db, business.id, status=status, limit=limit)
    
    return {
        "orders": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "status": o.status,
                "customer_name": o.customer.name,
                "customer_phone": o.customer.phone,
                "total": o.total,
                "item_count": o.item_count,
                "created_at": o.created_at.isoformat(),
                "estimated_delivery": o.estimated_delivery_time.isoformat() if o.estimated_delivery_time else None,
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "total_price": item.total_price
                    }
                    for item in o.items
                ]
            }
            for o in orders
        ]
    }


@app.get("/api/store/orders/{order_id}")
async def admin_get_order(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get single order details"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    order = get_order(db, order_id)
    if not order or order.business_id != business.id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "customer": {
            "name": order.customer.name,
            "phone": order.customer.phone,
            "total_orders": order.customer.total_orders,
            "total_spent": order.customer.total_spent
        },
        "items": [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "notes": item.notes
            }
            for item in order.items
        ],
        "pricing": {
            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total": order.total
        },
        "delivery": {
            "address": order.delivery_address,
            "instructions": order.delivery_instructions,
            "estimated_time": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        },
        "timestamps": {
            "created_at": order.created_at.isoformat(),
            "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
            "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None
        },
        "notes": {
            "customer": order.customer_notes,
            "business": order.business_notes
        }
    }


@app.put("/api/store/orders/{order_id}/status")
async def admin_update_order_status(
    request: Request,
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update order status"""
    user = get_current_user(request)
    business = get_business_by_user(db, user['id'])
    
    order = get_order(db, order_id)
    if not order or order.business_id != business.id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated = update_order_status(db, order_id, status)
    
    return {
        "status": "success",
        "order_id": updated.id,
        "new_status": updated.status
    }


@app.post("/api/store/setup")
async def setup_business(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(None),
    phone: str = Form(None),
    db: Session = Depends(get_db)
):
    """Initial business setup"""
    user = get_current_user(request)
    
    # Check if business already exists
    existing = get_business_by_user(db, user['id'])
    if existing:
        return {"status": "error", "message": "Business already exists"}
    
    # Check slug availability
    slug_taken = get_business_by_slug(db, slug)
    if slug_taken:
        return {"status": "error", "message": "Slug already taken"}
    
    business = create_business(
        db,
        user_id=user['id'],
        name=name,
        slug=slug,
        description=description,
        phone=phone
    )
    
    return {
        "status": "success",
        "business_id": business.id,
        "slug": business.slug
    }


@app.post("/api/store/demo-data")
async def create_demo_data_endpoint(request: Request, db: Session = Depends(get_db)):
    """Generate demo data (for testing)"""
    user = get_current_user(request)
    
    business = create_demo_store(db, user['id'])
    
    return {
        "status": "success",
        "business_id": business.id,
        "slug": business.slug,
        "message": f"Demo store '{business.name}' created!"
    }

# ═══════════════════════════════════════════════════════════════════
# STORE ROUTES - Add these to app.py
# ═══════════════════════════════════════════════════════════════════

@app.get("/store/{slug}/products")
async def storefront_products(
    slug: str,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get products for customer storefront"""
    business = get_business_by_slug(db, slug)
    
    if not business:
        raise HTTPException(status_code=404, detail="Store not found")
    
    products = list_products(
        db,
        business.id,
        category_id=category_id,
        active_only=True,
        in_stock_only=True
    )
    
    categories = list_categories(db, business.id, active_only=True)
    
    return {
        "categories": [
            {"id": c.id, "name": c.name, "icon": c.icon}
            for c in categories
        ],
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "unit": p.unit,
                "image_url": p.image_url,
                "in_stock": p.in_stock,
                "is_featured": p.is_featured
            }
            for p in products
        ]
    }


@app.post("/store/{slug}/chat")
async def storefront_chat(
    slug: str,
    message: str = Form(...),
    session_id: str = Form(...),
    cart: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """AI chat ordering"""
    business = get_business_by_slug(db, slug)
    
    if not business:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Parse cart if provided
    cart_data = json.loads(cart) if cart else {"items": []}
    
    # Build context
    context = {
        "cart": cart_data.get("items", []),
        "session_id": session_id
    }
    
    # Get AI response - pass db session correctly
    response = await chat_with_customer(
        message=message,
        business_id=business.id,
        db=db,  # Pass the actual db session
        context=context
    )
    
    return response


@app.get("/api/store/dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Admin dashboard stats"""
    # Get current user (use your existing auth)
    # user = get_current_user(request)
    
    # For testing, use user_id = 1
    business = get_business_by_user(db, user_id=1)
    
    if not business:
        return {"status": "no_business", "message": "No business found"}
    
    today_orders = get_today_orders(db, business.id)
    stats = get_order_stats(db, business.id, days=7)
    
    return {
        "business": {
            "name": business.name,
            "slug": business.slug,
            "is_open": business.is_open
        },
        "today": {
            "orders": len(today_orders),
            "revenue": sum(o.total for o in today_orders if o.status == 'delivered')
        },
        "week": stats
    }

@app.get("/store/{slug}", response_class=HTMLResponse)
async def storefront_home(slug: str, request: Request, db: Session = Depends(get_db)):
    """Customer landing page"""
    business = get_business_by_slug(db, slug)
    
    if not business:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return templates.TemplateResponse("storefront/store.html", {
        "request": request,
        "business": business
    })


@app.get("/store/{slug}/cart", response_class=HTMLResponse)
async def storefront_cart(slug: str, request: Request):
    """Cart and checkout page"""
    return templates.TemplateResponse("storefront/cart.html", {
        "request": request
    })

@app.post("/store/{slug}/orders")
async def storefront_place_order(
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Place a new order"""
    business = get_business_by_slug(db, slug)
    
    if not business:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if not business.is_open:
        return {"status": "error", "message": "Store is currently closed"}
    
    # Get JSON body
    body = await request.json()
    
    # Get or create customer
    customer = get_or_create_customer(
        db,
        business.id,
        body['customer_phone'],
        body.get('customer_name')
    )
    
    # Create order
    order = create_order(
        db,
        business_id=business.id,
        customer_id=customer.id,
        items=body['items'],
        delivery_address=body['delivery_address'],
        customer_notes=body.get('customer_notes'),
        delivery_instructions=body.get('delivery_instructions')
    )
    
    return {
        "status": "success",
        "order_number": order.order_number,
        "order_id": order.id,
        "total": order.total,
        "estimated_delivery": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
    }


@app.get("/store/{slug}/orders/{order_number}")
async def storefront_track_order(
    slug: str,
    order_number: str,
    db: Session = Depends(get_db)
):
    """Track order status (API endpoint for AJAX)"""
    business = get_business_by_slug(db, slug)
    
    if not business:
        raise HTTPException(status_code=404, detail="Store not found")
    
    order = get_order_by_number(db, order_number)
    
    if not order or order.business_id != business.id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order_number": order.order_number,
        "status": order.status,
        "items": [
            {
                "name": item.product_name,
                "quantity": item.quantity,
                "total": item.total_price
            }
            for item in order.items
        ],
        "customer": {
            "phone": order.customer.phone
        },
        "total": order.total,
        "delivery": {
            "address": order.delivery_address,
            "estimated_time": order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None
        },
        "pricing": {
            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "total": order.total
        },
        "timestamps": {
            "created_at": order.created_at.isoformat(),
            "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
            "preparing_at": order.preparing_started_at.isoformat() if order.preparing_started_at else None,
            "ready_at": order.ready_at.isoformat() if order.ready_at else None,
            "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None
        }
    }