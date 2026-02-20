# ═══════════════════════════════════════════════════════════════════
# MINIMAL WORKING CRUD_STORE - Essential Functions Only
# ═══════════════════════════════════════════════════════════════════
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional

from database.models import (
    Business, StoreCategory, StoreProduct, StoreCustomer, 
    StoreOrder, StoreOrderItem, StoreChatMessage
)


# ═══════════════════════════════════════════════════════════════════
# BUSINESS OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def get_business_by_user(db: Session, user_id: int) -> Optional[Business]:
    """Get business for a user"""
    return db.query(Business).filter(Business.user_id == user_id).first()


def get_business_by_slug(db: Session, slug: str) -> Optional[Business]:
    """Get business by storefront slug"""
    return db.query(Business).filter(Business.slug == slug).first()


def create_business(db: Session, user_id: int, name: str, slug: str, **kwargs) -> Business:
    """Create a new business"""
    business = Business(user_id=user_id, name=name, slug=slug, **kwargs)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


# ═══════════════════════════════════════════════════════════════════
# CATEGORY OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def list_categories(db: Session, business_id: int, active_only: bool = True) -> List[StoreCategory]:
    """List all categories for a business"""
    query = db.query(StoreCategory).filter(StoreCategory.business_id == business_id)
    if active_only:
        query = query.filter(StoreCategory.is_active == True)
    return query.order_by(StoreCategory.display_order).all()


def create_category(db: Session, business_id: int, name: str, **kwargs) -> StoreCategory:
    """Create a product category"""
    category = StoreCategory(business_id=business_id, name=name, **kwargs)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


# ═══════════════════════════════════════════════════════════════════
# PRODUCT OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def list_products(db: Session, business_id: int, category_id: int = None, 
                 active_only: bool = True, in_stock_only: bool = False) -> List[StoreProduct]:
    """List products with filters"""
    query = db.query(StoreProduct).filter(StoreProduct.business_id == business_id)
    
    if category_id:
        query = query.filter(StoreProduct.category_id == category_id)
    if active_only:
        query = query.filter(StoreProduct.is_active == True)
    if in_stock_only:
        query = query.filter(StoreProduct.in_stock == True)
    
    return query.order_by(StoreProduct.display_order, StoreProduct.created_at.desc()).all()


def get_product(db: Session, product_id: int) -> Optional[StoreProduct]:
    """Get a specific product"""
    return db.query(StoreProduct).filter(StoreProduct.id == product_id).first()


def create_product(db: Session, business_id: int, name: str, price: float, **kwargs) -> StoreProduct:
    """Create a new product"""
    product = StoreProduct(business_id=business_id, name=name, price=price, **kwargs)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, **kwargs) -> StoreProduct:
    """Update a product"""
    product = get_product(db, product_id)
    if product:
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(product)
    return product


def search_products(db: Session, business_id: int, search_term: str) -> List[StoreProduct]:
    """Search products by name or description"""
    search = f"%{search_term}%"
    return db.query(StoreProduct).filter(
        StoreProduct.business_id == business_id,
        StoreProduct.is_active == True,
        (StoreProduct.name.ilike(search) | StoreProduct.description.ilike(search))
    ).all()


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def get_or_create_customer(db: Session, business_id: int, phone: str, 
                          name: str = None, email: str = None) -> StoreCustomer:
    """Get existing customer or create new one"""
    customer = db.query(StoreCustomer).filter(
        StoreCustomer.business_id == business_id,
        StoreCustomer.phone == phone
    ).first()
    
    if not customer:
        customer = StoreCustomer(
            business_id=business_id,
            phone=phone,
            name=name,
            email=email,
            first_order_date=datetime.utcnow()
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    return customer


# ═══════════════════════════════════════════════════════════════════
# ORDER OPERATIONS
# ═══════════════════════════════════════════════════════════════════

def generate_order_number(db: Session) -> str:
    """Generate unique order number"""
    date_str = datetime.utcnow().strftime("%Y%m%d")
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    count = db.query(StoreOrder).filter(StoreOrder.created_at >= today_start).count()
    return f"ORD-{date_str}-{count+1:03d}"


def create_order(db: Session, business_id: int, customer_id: int, 
                items: List[dict], delivery_address: dict, **kwargs) -> StoreOrder:
    """Create a new order"""
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for item_data in items:
        product = get_product(db, item_data['product_id'])
        if not product:
            continue
        
        quantity = item_data['quantity']
        unit_price = product.price
        total_price = unit_price * quantity
        subtotal += total_price
        
        order_items.append({
            'product_id': product.id,
            'product_name': product.name,
            'product_image_url': product.image_url,
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
            'unit': product.unit,
            'notes': item_data.get('notes')
        })
    
    # Get delivery fee
    business = db.query(Business).filter(Business.id == business_id).first()
    delivery_fee = 0
    if business and subtotal < business.free_delivery_above:
        delivery_fee = business.delivery_fee
    
    total = subtotal + delivery_fee
    
    # Create order
    order = StoreOrder(
        business_id=business_id,
        customer_id=customer_id,
        order_number=generate_order_number(db),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        delivery_address=delivery_address,
        estimated_delivery_time=datetime.utcnow() + timedelta(hours=1),
        **kwargs
    )
    db.add(order)
    db.flush()
    
    # Create order items
    for item_data in order_items:
        order_item = StoreOrderItem(order_id=order.id, **item_data)
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Optional[StoreOrder]:
    """Get order by ID"""
    return db.query(StoreOrder).filter(StoreOrder.id == order_id).first()


def get_order_by_number(db: Session, order_number: str) -> Optional[StoreOrder]:
    """Get order by order number"""
    return db.query(StoreOrder).filter(StoreOrder.order_number == order_number).first()


def list_orders(db: Session, business_id: int, status: str = None, 
               limit: int = 50, offset: int = 0) -> List[StoreOrder]:
    """List orders with filters"""
    query = db.query(StoreOrder).filter(StoreOrder.business_id == business_id)
    
    if status:
        query = query.filter(StoreOrder.status == status)
    
    return query.order_by(desc(StoreOrder.created_at)).limit(limit).offset(offset).all()


def update_order_status(db: Session, order_id: int, new_status: str) -> StoreOrder:
    """Update order status"""
    order = get_order(db, order_id)
    if order:
        order.status = new_status
        
        if new_status == 'confirmed':
            order.confirmed_at = datetime.utcnow()
        elif new_status == 'preparing':
            order.preparing_started_at = datetime.utcnow()
        elif new_status == 'ready':
            order.ready_at = datetime.utcnow()
        elif new_status == 'delivered':
            order.delivered_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
    return order


def get_today_orders(db: Session, business_id: int) -> List[StoreOrder]:
    """Get all orders placed today"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(StoreOrder).filter(
        StoreOrder.business_id == business_id,
        StoreOrder.created_at >= today_start
    ).order_by(desc(StoreOrder.created_at)).all()


def get_order_stats(db: Session, business_id: int, days: int = 7) -> dict:
    """Get order statistics"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    orders = db.query(StoreOrder).filter(
        StoreOrder.business_id == business_id,
        StoreOrder.created_at >= cutoff
    ).all()
    
    return {
        'total_orders': len(orders),
        'pending': len([o for o in orders if o.status == 'pending']),
        'delivered': len([o for o in orders if o.status == 'delivered']),
        'total_revenue': sum(o.total for o in orders if o.status == 'delivered'),
        'avg_order_value': sum(o.total for o in orders) / len(orders) if orders else 0
    }


def get_popular_products(db: Session, business_id: int, limit: int = 10) -> List[tuple]:
    """Get most ordered products"""
    return db.query(
        StoreProduct.id,
        StoreProduct.name,
        StoreProduct.times_ordered,
        StoreProduct.total_revenue
    ).filter(
        StoreProduct.business_id == business_id
    ).order_by(desc(StoreProduct.times_ordered)).limit(limit).all()


def get_customer_by_phone(db: Session, business_id: int, phone: str) -> Optional[StoreCustomer]:
    """Get customer by phone number"""
    return db.query(StoreCustomer).filter(
        StoreCustomer.business_id == business_id,
        StoreCustomer.phone == phone
    ).first()