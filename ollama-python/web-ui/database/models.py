from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    picture_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    settings = Column(JSON, default=dict)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    pdfs = relationship("PDF", back_populates="user", cascade="all, delete-orphan")
    email_drafts = relationship("EmailDraft", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    tokens_used = Column(Integer)
    model = Column(String, default="llama3.2:latest")
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', preview='{self.content[:30]}...')>"


class PDF(Base):
    __tablename__ = 'pdfs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)
    page_count = Column(Integer)
    chunk_count = Column(Integer)
    collection_name = Column(String, unique=True)  # ChromaDB collection name
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_accessed = Column(DateTime)
    status = Column(String, default='ready')  # 'uploading', 'processing', 'ready', 'error'
    
    # Relationships
    user = relationship("User", back_populates="pdfs")
    queries = relationship("PDFQuery", back_populates="pdf", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PDF(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"


class PDFQuery(Base):
    __tablename__ = 'pdf_queries'
    
    id = Column(Integer, primary_key=True)
    pdf_id = Column(Integer, ForeignKey('pdfs.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    pdf = relationship("PDF", back_populates="queries")

    def __repr__(self):
        return f"<PDFQuery(id={self.id}, question='{self.question[:30]}...')>"


class EmailDraft(Base):
    __tablename__ = 'email_drafts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    description = Column(Text)
    tone = Column(String)
    subject = Column(String)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_template = Column(Boolean, default=False)
    template_name = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="email_drafts")

    def __repr__(self):
        return f"<EmailDraft(id={self.id}, subject='{self.subject}')>"


class UsageLog(Base):
    __tablename__ = 'usage_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    tool = Column(String, nullable=False)  # 'chat', 'email', 'pdf'
    action = Column(String)  # 'message_sent', 'pdf_uploaded', 'email_generated', etc
    extra_data = Column(JSON)  # Flexible JSON for tool-specific data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, tool='{self.tool}', action='{self.action}')>"
