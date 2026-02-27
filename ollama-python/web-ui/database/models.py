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

# ═══════════════════════════════════════════════════════════════════
# FOOD ORDERING STORE - DATABASE MODELS
# ═══════════════════════════════════════════════════════════════════
# 
# Add these models to your existing database/models.py file
# These work alongside your existing User, Conversation, Message, PDF models
#
# ═══════════════════════════════════════════════════════════════════

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
#from database.models import Base  # Import your existing Base


# ═══════════════════════════════════════════════════════════════════
# BUSINESS MODEL
# ═══════════════════════════════════════════════════════════════════

class Business(Base):
    """
    One business per user (connected to existing User model)
    Represents a food business/store (e.g., "Amma's Kitchen")
    """
    __tablename__ = 'businesses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    
    # Business Info
    name = Column(String(200), nullable=False)  # "Amma's Kitchen"
    description = Column(Text)  # "Fresh homemade South Indian food"
    phone = Column(String(20))  # "+91 98765 43210"
    email = Column(String(200))
    
    # Branding
    logo_url = Column(String(500))  # Path to logo image
    cover_image_url = Column(String(500))  # Header banner image
    primary_color = Column(String(7), default='#00C853')  # Brand color (hex)
    
    # Business Settings
    is_open = Column(Boolean, default=True)  # Currently accepting orders?
    min_order_value = Column(Float, default=0)  # Minimum order amount
    delivery_fee = Column(Float, default=0)  # Delivery charge
    free_delivery_above = Column(Float, default=500)  # Free delivery threshold
    
    # Storefront
    slug = Column(String(100), unique=True, nullable=False, index=True)  # URL: /store/ammas-kitchen
    storefront_enabled = Column(Boolean, default=True)
    
    # Stats (auto-updated)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])  # Link to existing User model
    categories = relationship("StoreCategory", back_populates="business", cascade="all, delete-orphan", order_by="StoreCategory.display_order")
    products = relationship("StoreProduct", back_populates="business", cascade="all, delete-orphan")
    orders = relationship("StoreOrder", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("StoreCustomer", back_populates="business", cascade="all, delete-orphan")
    chat_messages = relationship("StoreChatMessage", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.name}', slug='{self.slug}')>"


# ═══════════════════════════════════════════════════════════════════
# CATEGORY MODEL
# ═══════════════════════════════════════════════════════════════════

class StoreCategory(Base):
    """
    Product categories (e.g., "Batters", "Flours", "Snacks")
    Used to organize products in the storefront
    """
    __tablename__ = 'store_categories'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False, index=True)
    
    # Category Info
    name = Column(String(100), nullable=False)  # "Batters"
    description = Column(Text)  # Optional description
    icon = Column(String(10))  # Emoji icon: "🥞"
    
    # Display
    display_order = Column(Integer, default=0)  # Sort order (lower = first)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="categories")
    products = relationship("StoreProduct", back_populates="category", order_by="StoreProduct.display_order")

    def __repr__(self):
        return f"<StoreCategory(id={self.id}, name='{self.name}')>"


# ═══════════════════════════════════════════════════════════════════
# PRODUCT MODEL
# ═══════════════════════════════════════════════════════════════════

class StoreProduct(Base):
    """
    Products/items for sale (e.g., "IDLI/DOSA Batter")
    """
    __tablename__ = 'store_products'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('store_categories.id'), index=True)
    
    # Basic Info
    name = Column(String(200), nullable=False)  # "IDLI/DOSA Batter"
    description = Column(Text)  # "Fresh homemade batter..."
    image_url = Column(String(500))  # "/static/uploads/products/idli-batter.jpg"
    
    # Pricing
    price = Column(Float, nullable=False)  # 50.00
    original_price = Column(Float)  # For showing discounts (e.g., was ₹60, now ₹50)
    unit = Column(String(50))  # "1/2 kg", "250g", "1 piece"
    
    # Inventory
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer)  # Optional: exact quantity tracking
    low_stock_threshold = Column(Integer, default=5)  # Alert when stock < this
    
    # Additional Info
    tags = Column(JSON)  # ["vegan", "gluten-free", "organic"]
    preparation_time = Column(Integer)  # Minutes (optional)
    
    # Stats (auto-updated)
    times_ordered = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Display
    is_featured = Column(Boolean, default=False)  # Show on home page?
    is_active = Column(Boolean, default=True)  # Visible to customers?
    display_order = Column(Integer, default=0)  # Sort order
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="products")
    category = relationship("StoreCategory", back_populates="products")
    order_items = relationship("StoreOrderItem", back_populates="product")

    def __repr__(self):
        return f"<StoreProduct(id={self.id}, name='{self.name}', price={self.price})>"
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if original_price is set"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER MODEL
# ═══════════════════════════════════════════════════════════════════

class StoreCustomer(Base):
    """
    Customers who place orders
    Identified by phone number (no login required for customers)
    """
    __tablename__ = 'store_customers'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False, index=True)
    
    # Contact Info (phone is primary identifier)
    phone = Column(String(20), nullable=False, index=True)  # "+91 98765 43210"
    name = Column(String(200))  # Collected during first order
    email = Column(String(200))
    
    # Saved Addresses (JSON array)
    # Format: [{"label": "Home", "address": "123 Main St", "default": true}, ...]
    addresses = Column(JSON, default=list)
    
    # Preferences
    dietary_restrictions = Column(JSON)  # ["gluten-free", "vegan"]
    favorite_products = Column(JSON)  # [product_id1, product_id2, ...]
    
    # Stats (auto-updated)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    
    # Engagement
    first_order_date = Column(DateTime)
    is_regular = Column(Boolean, default=False)  # Auto-set if 3+ orders
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    business = relationship("Business", back_populates="customers")
    orders = relationship("StoreOrder", back_populates="customer", order_by="StoreOrder.created_at.desc()")

    def __repr__(self):
        return f"<StoreCustomer(id={self.id}, name='{self.name}', phone='{self.phone}')>"


# ═══════════════════════════════════════════════════════════════════
# ORDER MODEL
# ═══════════════════════════════════════════════════════════════════

class StoreOrder(Base):
    """
    Customer orders
    Status flow: pending → confirmed → preparing → ready → delivered
    """
    __tablename__ = 'store_orders'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('store_customers.id'), nullable=False, index=True)
    
    # Order Info
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # "ORD-20250220-001"
    
    # Status Management
    # Flow: pending → confirmed → preparing → ready → out_for_delivery → delivered
    # Can also be: cancelled, failed
    status = Column(String(50), default='pending', index=True)
    
    # Pricing
    subtotal = Column(Float, nullable=False)  # Sum of all items
    delivery_fee = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)  # subtotal + delivery - discount
    
    # Payment
    payment_method = Column(String(50), default='cod')  # cod, online, upi
    payment_status = Column(String(50), default='pending')  # pending, paid, failed, refunded
    
    # Delivery Info
    delivery_address = Column(JSON, nullable=False)  # Full address object
    # Format: {"address": "123 Main St", "city": "Bangalore", "pincode": "560001"}
    delivery_instructions = Column(Text)  # "Ring bell twice", "Leave at door"
    estimated_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    
    # Communication
    customer_notes = Column(Text)  # Special requests from customer
    business_notes = Column(Text)  # Internal notes
    conversation_summary = Column(Text)  # If ordered via AI chat, summary of conversation
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    confirmed_at = Column(DateTime)
    preparing_started_at = Column(DateTime)
    ready_at = Column(DateTime)
    delivered_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    business = relationship("Business", back_populates="orders")
    customer = relationship("StoreCustomer", back_populates="orders")
    items = relationship("StoreOrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StoreOrder(id={self.id}, order_number='{self.order_number}', status='{self.status}', total={self.total})>"
    
    @property
    def item_count(self):
        """Total number of items (considering quantities)"""
        return sum(item.quantity for item in self.items)


# ═══════════════════════════════════════════════════════════════════
# ORDER ITEM MODEL
# ═══════════════════════════════════════════════════════════════════

class StoreOrderItem(Base):
    """
    Individual items within an order
    Stores snapshot of product details at time of order (in case product changes/deleted later)
    """
    __tablename__ = 'store_order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('store_orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('store_products.id'))  # Nullable (product might be deleted)
    
    # Product Snapshot (captured at order time)
    product_name = Column(String(200), nullable=False)
    product_image_url = Column(String(500))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)  # quantity * unit_price
    unit = Column(String(50))  # "1/2 kg"
    
    # Special Instructions (per item)
    notes = Column(Text)  # "Extra spicy", "No onions"
    
    # Relationships
    order = relationship("StoreOrder", back_populates="items")
    product = relationship("StoreProduct", back_populates="order_items")

    def __repr__(self):
        return f"<StoreOrderItem(id={self.id}, product='{self.product_name}', qty={self.quantity}, price={self.total_price})>"


# ═══════════════════════════════════════════════════════════════════
# CHAT MESSAGE MODEL (for AI ordering)
# ═══════════════════════════════════════════════════════════════════

class StoreChatMessage(Base):
    """
    Stores chat messages for AI-powered ordering
    Helps maintain conversation context and learn from patterns
    """
    __tablename__ = 'store_chat_messages'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False, index=True)
    
    # Session Tracking
    session_id = Column(String(100), nullable=False, index=True)  # Browser session UUID
    customer_phone = Column(String(20))  # If customer identified
    
    # Message
    role = Column(String(20), nullable=False)  # 'customer' or 'assistant'
    message = Column(Text, nullable=False)
    
    # Context (for AI learning)
    suggested_products = Column(JSON)  # Products AI suggested in this message
    cart_snapshot = Column(JSON)  # Cart state at this point
    intent = Column(String(50))  # 'browse', 'add_to_cart', 'question', 'checkout'
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    business = relationship("Business")

    def __repr__(self):
        return f"<StoreChatMessage(id={self.id}, role='{self.role}', session='{self.session_id}')>"


# ═══════════════════════════════════════════════════════════════════
# INDEXES FOR PERFORMANCE
# ═══════════════════════════════════════════════════════════════════

# Additional composite indexes (add these to your migration or init_db.py)
# from sqlalchemy import Index
# 
# Index('idx_business_user', Business.user_id)
# Index('idx_product_business_category', StoreProduct.business_id, StoreProduct.category_id)
# Index('idx_order_business_status', StoreOrder.business_id, StoreOrder.status)
# Index('idx_order_customer_date', StoreOrder.customer_id, StoreOrder.created_at.desc())
# Index('idx_customer_business_phone', StoreCustomer.business_id, StoreCustomer.phone)
