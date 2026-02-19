from sqlalchemy.orm import Session
from database.models import User, Conversation, Message, PDF, PDFQuery, EmailDraft, UsageLog
from datetime import datetime
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════════
# USER OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def get_or_create_user(db: Session, email: str, name: str = None, picture_url: str = None) -> User:
    """Get existing user or create new one. Updates last_login."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            name=name,
            picture_url=picture_url,
            last_login=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        if name:
            user.name = name
        if picture_url:
            user.picture_url = picture_url
        db.commit()
    
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def create_conversation(db: Session, user_id: int, title: str = None) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
    """Get a specific conversation (with user ownership check)."""
    return db.query(Conversation)\
        .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)\
        .first()


def get_user_conversations(db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Conversation]:
    """Get all conversations for a user, ordered by most recent."""
    return db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.updated_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    """Delete a conversation (with user ownership check)."""
    conversation = get_conversation(db, conversation_id, user_id)
    if conversation:
        db.delete(conversation)
        db.commit()
        return True
    return False


def search_conversations(db: Session, user_id: int, query: str, limit: int = 10) -> List[Conversation]:
    """Search conversations by title or message content."""
    return db.query(Conversation)\
        .join(Message)\
        .filter(
            Conversation.user_id == user_id,
            (Conversation.title.ilike(f"%{query}%")) | (Message.content.ilike(f"%{query}%"))
        )\
        .distinct()\
        .order_by(Conversation.updated_at.desc())\
        .limit(limit)\
        .all()


# ═══════════════════════════════════════════════════════════════════
# MESSAGE OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    model: str = "llama3.2:latest",
    tokens_used: int = None
) -> Message:
    """Add a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        model=model,
        tokens_used=tokens_used
    )
    db.add(message)
    
    # Update conversation metadata
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.message_count += 1
        conversation.updated_at = datetime.utcnow()
        
        # Auto-generate title from first user message
        if conversation.message_count == 1 and role == "user":
            conversation.title = content[:50] + ("..." if len(content) > 50 else "")
    
    db.commit()
    db.refresh(message)
    return message


def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
    """Get all messages in a conversation, ordered chronologically."""
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at.asc())\
        .all()


def get_recent_messages(db: Session, conversation_id: int, limit: int = 10) -> List[Message]:
    """Get recent messages from a conversation."""
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .all()


# ═══════════════════════════════════════════════════════════════════
# PDF OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def create_pdf_record(
    db: Session,
    user_id: int,
    filename: str,
    original_filename: str,
    file_size: int,
    page_count: int,
    chunk_count: int,
    collection_name: str
) -> PDF:
    """Create a PDF record in the database."""
    pdf = PDF(
        user_id=user_id,
        filename=filename,
        original_filename=original_filename,
        file_size=file_size,
        page_count=page_count,
        chunk_count=chunk_count,
        collection_name=collection_name,
        status='ready'
    )
    db.add(pdf)
    db.commit()
    db.refresh(pdf)
    return pdf


def get_pdf_by_id(db: Session, pdf_id: int, user_id: int) -> Optional[PDF]:
    """Get a PDF by ID (with user ownership check)."""
    return db.query(PDF)\
        .filter(PDF.id == pdf_id, PDF.user_id == user_id)\
        .first()


def get_user_pdfs(db: Session, user_id: int, limit: int = 50) -> List[PDF]:
    """Get all PDFs for a user."""
    return db.query(PDF)\
        .filter(PDF.user_id == user_id)\
        .order_by(PDF.uploaded_at.desc())\
        .limit(limit)\
        .all()


def update_pdf_access(db: Session, pdf_id: int, user_id: int):
    """Update the last_accessed timestamp for a PDF."""
    pdf = get_pdf_by_id(db, pdf_id, user_id)
    if pdf:
        pdf.last_accessed = datetime.utcnow()
        db.commit()


def delete_pdf(db: Session, pdf_id: int, user_id: int) -> bool:
    """Delete a PDF record (with user ownership check)."""
    pdf = get_pdf_by_id(db, pdf_id, user_id)
    if pdf:
        db.delete(pdf)
        db.commit()
        return True
    return False


def add_pdf_query(db: Session, pdf_id: int, user_id: int, question: str, answer: str) -> PDFQuery:
    """Log a PDF query."""
    query = PDFQuery(
        pdf_id=pdf_id,
        user_id=user_id,
        question=question,
        answer=answer
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def get_pdf_queries(db: Session, pdf_id: int, user_id: int, limit: int = 20) -> List[PDFQuery]:
    """Get query history for a PDF."""
    return db.query(PDFQuery)\
        .filter(PDFQuery.pdf_id == pdf_id, PDFQuery.user_id == user_id)\
        .order_by(PDFQuery.created_at.desc())\
        .limit(limit)\
        .all()


# ═══════════════════════════════════════════════════════════════════
# EMAIL DRAFT OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def create_email_draft(
    db: Session,
    user_id: int,
    description: str,
    tone: str,
    subject: str,
    body: str,
    is_template: bool = False,
    template_name: str = None
) -> EmailDraft:
    """Create an email draft."""
    draft = EmailDraft(
        user_id=user_id,
        description=description,
        tone=tone,
        subject=subject,
        body=body,
        is_template=is_template,
        template_name=template_name
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def get_user_drafts(db: Session, user_id: int, include_templates: bool = False, limit: int = 20) -> List[EmailDraft]:
    """Get email drafts for a user."""
    query = db.query(EmailDraft).filter(EmailDraft.user_id == user_id)
    
    if not include_templates:
        query = query.filter(EmailDraft.is_template == False)
    
    return query.order_by(EmailDraft.created_at.desc()).limit(limit).all()


def get_email_templates(db: Session, user_id: int) -> List[EmailDraft]:
    """Get email templates for a user."""
    return db.query(EmailDraft)\
        .filter(EmailDraft.user_id == user_id, EmailDraft.is_template == True)\
        .order_by(EmailDraft.created_at.desc())\
        .all()


def delete_email_draft(db: Session, draft_id: int, user_id: int) -> bool:
    """Delete an email draft."""
    draft = db.query(EmailDraft)\
        .filter(EmailDraft.id == draft_id, EmailDraft.user_id == user_id)\
        .first()
    if draft:
        db.delete(draft)
        db.commit()
        return True
    return False


# ═══════════════════════════════════════════════════════════════════
# USAGE LOG OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def log_usage(db: Session, user_id: int, tool: str, action: str, extra_data: dict = None):
    """Log a usage event."""
    log = UsageLog(
        user_id=user_id,
        tool=tool,
        action=action,
        extra_data=extra_data
    )
    db.add(log)
    db.commit()


def get_user_usage_stats(db: Session, user_id: int, days: int = 30) -> dict:
    """Get usage statistics for a user."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(UsageLog)\
        .filter(UsageLog.user_id == user_id, UsageLog.created_at >= cutoff)\
        .all()
    
    stats = {
        'total_actions': len(logs),
        'by_tool': {},
        'by_action': {}
    }
    
    for log in logs:
        stats['by_tool'][log.tool] = stats['by_tool'].get(log.tool, 0) + 1
        stats['by_action'][log.action] = stats['by_action'].get(log.action, 0) + 1
    
    return stats
