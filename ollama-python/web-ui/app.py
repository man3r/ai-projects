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