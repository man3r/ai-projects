# ═══════════════════════════════════════════════════════════════════
# DEMO DATA GENERATOR - Food Ordering Store (CORRECTED VERSION)
# ═══════════════════════════════════════════════════════════════════

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database.models import Business, StoreCategory, StoreProduct, StoreCustomer, StoreOrder, StoreOrderItem
import random


def create_demo_store(db: Session, user_id: int) -> Business:
    """
    Create a complete demo store with products, customers, and sample orders
    """
    
    print("🏗️  Creating demo store...")
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. CREATE BUSINESS
    # ═══════════════════════════════════════════════════════════════════
    
    business = Business(
        user_id=user_id,
        name="Amma's Kitchen",
        description="Fresh homemade South Indian food delivered to your door",
        phone="+91 98765 43210",
        email="contact@ammaskitchen.com",
        slug="ammas-kitchen",
        is_open=True,
        min_order_value=100,
        delivery_fee=30,
        free_delivery_above=300,
        primary_color="#00C853",
        storefront_enabled=True
    )
    db.add(business)
    db.flush()  # Get business.id
    
    print(f"✅ Created business: {business.name} (slug: {business.slug})")
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. CREATE CATEGORIES
    # ═══════════════════════════════════════════════════════════════════
    
    categories = [
        StoreCategory(
            business_id=business.id,
            name="Batters",
            icon="🥞",
            description="Fermented batters for idli, dosa, and more",
            display_order=1,
            is_active=True
        ),
        StoreCategory(
            business_id=business.id,
            name="Flours",
            icon="🌾",
            description="Fresh ground flours and atta",
            display_order=2,
            is_active=True
        ),
        StoreCategory(
            business_id=business.id,
            name="Flakes",
            icon="🫘",
            description="Healthy breakfast flakes",
            display_order=3,
            is_active=True
        ),
        StoreCategory(
            business_id=business.id,
            name="Snacks",
            icon="🍿",
            description="Traditional South Indian snack mixes",
            display_order=4,
            is_active=True
        )
    ]
    
    for cat in categories:
        db.add(cat)
    db.flush()
    
    print(f"✅ Created {len(categories)} categories")
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. CREATE PRODUCTS
    # ═══════════════════════════════════════════════════════════════════
    
    products = [
        # BATTERS
        StoreProduct(
            business_id=business.id,
            category_id=categories[0].id,
            name="IDLI/DOSA Batter",
            description="Fresh homemade batter made with organic rice and urad dal. Perfectly fermented for soft idlis and crispy dosas. Makes approximately 20 idlis.",
            price=50.00,
            original_price=60.00,
            unit="1/2 kg",
            image_url="/static/uploads/products/idli-batter.jpg",
            in_stock=True,
            stock_quantity=12,
            is_featured=True,
            times_ordered=156
        ),
        StoreProduct(
            business_id=business.id,
            category_id=categories[0].id,
            name="Dosa Mix Batter",
            description="Crispy dosa batter with perfect fermentation. Made with premium rice and lentils.",
            price=60.00,
            unit="1 kg",
            image_url="/static/uploads/products/dosa-batter.jpg",
            in_stock=True,
            stock_quantity=8,
            times_ordered=98
        ),
        StoreProduct(
            business_id=business.id,
            category_id=categories[0].id,
            name="SPECIAL IDLI Batter",
            description="Premium blend with extra softness. Customer favorite!",
            price=55.00,
            unit="1/2 kg",
            image_url="/static/uploads/products/special-idli.jpg",
            in_stock=True,
            stock_quantity=5,
            is_featured=True,
            times_ordered=45
        ),
        
        # FLOURS
        StoreProduct(
            business_id=business.id,
            category_id=categories[1].id,
            name="Rice Flour",
            description="Fine ground rice flour perfect for dosas and snacks. Stone-ground to preserve nutrients.",
            price=40.00,
            unit="500g",
            image_url="/static/uploads/products/rice-flour.jpg",
            in_stock=True,
            stock_quantity=15
        ),
        StoreProduct(
            business_id=business.id,
            category_id=categories[1].id,
            name="Wheat Flour (Atta)",
            description="Stone-ground whole wheat flour. Perfect for chapatis and parathas.",
            price=45.00,
            unit="1 kg",
            image_url="/static/uploads/products/wheat-flour.jpg",
            in_stock=True,
            stock_quantity=20
        ),
        
        # FLAKES
        StoreProduct(
            business_id=business.id,
            category_id=categories[2].id,
            name="Wheat Flakes (Aval)",
            description="Healthy breakfast flakes. Rich in fiber and easy to digest.",
            price=125.00,
            unit="250g",
            image_url="/static/uploads/products/wheat-flakes.jpg",
            in_stock=True,
            stock_quantity=10,
            is_featured=True,
            times_ordered=89
        ),
        StoreProduct(
            business_id=business.id,
            category_id=categories[2].id,
            name="Rice Flakes (Poha)",
            description="Light and fluffy rice flakes. Perfect for quick breakfast.",
            price=115.00,
            unit="500g",
            image_url="/static/uploads/products/rice-flakes.jpg",
            in_stock=True,
            stock_quantity=14
        ),
        
        # SNACKS
        StoreProduct(
            business_id=business.id,
            category_id=categories[3].id,
            name="Murukku Mix",
            description="Traditional savory snack mix. Just add water and fry for crispy murukku.",
            price=80.00,
            unit="500g",
            image_url="/static/uploads/products/murukku-mix.jpg",
            in_stock=True,
            stock_quantity=8
        )
    ]
    
    for product in products:
        db.add(product)
    db.flush()
    
    print(f"✅ Created {len(products)} products")
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. CREATE SAMPLE CUSTOMERS
    # ═══════════════════════════════════════════════════════════════════
    
    customers = [
        StoreCustomer(
            business_id=business.id,
            phone="+91 98765 11111",
            name="Ramesh Kumar",
            email="ramesh.kumar@email.com",
            addresses=[
                {
                    "label": "Home",
                    "address": "123 Main Street, Koramangala, Bangalore 560001",
                    "default": True
                }
            ],
            total_orders=12,
            total_spent=2680.00,
            first_order_date=datetime.utcnow() - timedelta(days=90),
            is_regular=True
        ),
        StoreCustomer(
            business_id=business.id,
            phone="+91 98765 22222",
            name="Priya Singh",
            email="priya.singh@email.com",
            addresses=[
                {
                    "label": "Home",
                    "address": "789 Lake View, Bangalore 560002",
                    "default": True
                }
            ],
            total_orders=8,
            total_spent=1450.00,
            first_order_date=datetime.utcnow() - timedelta(days=60),
            is_regular=True
        )
    ]
    
    for customer in customers:
        db.add(customer)
    db.flush()
    
    print(f"✅ Created {len(customers)} sample customers")
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. CREATE SAMPLE ORDERS
    # ═══════════════════════════════════════════════════════════════════
    
    # Order 1: Delivered
    order1 = StoreOrder(
        business_id=business.id,
        customer_id=customers[0].id,
        order_number="ORD-20250218-001",
        status="delivered",
        subtotal=230.00,
        delivery_fee=0,
        total=230.00,
        payment_method="cod",
        payment_status="paid",
        delivery_address=customers[0].addresses[0],
        created_at=datetime.utcnow() - timedelta(days=2),
        delivered_at=datetime.utcnow() - timedelta(days=2, hours=-2)
    )
    db.add(order1)
    db.flush()
    
    order1_items = [
        StoreOrderItem(
            order_id=order1.id,
            product_id=products[0].id,
            product_name="IDLI/DOSA Batter",
            quantity=2,
            unit_price=50.00,
            total_price=100.00
        ),
        StoreOrderItem(
            order_id=order1.id,
            product_id=products[5].id,
            product_name="Wheat Flakes (Aval)",
            quantity=1,
            unit_price=125.00,
            total_price=125.00
        )
    ]
    for item in order1_items:
        db.add(item)
    
    # Order 2: Preparing
    order2 = StoreOrder(
        business_id=business.id,
        customer_id=customers[1].id,
        order_number="ORD-20250220-001",
        status="preparing",
        subtotal=310.00,
        delivery_fee=30,
        total=340.00,
        payment_method="cod",
        delivery_address=customers[1].addresses[0],
        created_at=datetime.utcnow() - timedelta(minutes=45)
    )
    db.add(order2)
    db.flush()
    
    order2_items = [
        StoreOrderItem(
            order_id=order2.id,
            product_id=products[1].id,
            product_name="Dosa Mix Batter",
            quantity=2,
            unit_price=60.00,
            total_price=120.00
        ),
        StoreOrderItem(
            order_id=order2.id,
            product_id=products[4].id,
            product_name="Wheat Flour (Atta)",
            quantity=3,
            unit_price=45.00,
            total_price=135.00
        )
    ]
    for item in order2_items:
        db.add(item)
    
    # Order 3: Pending
    order3 = StoreOrder(
        business_id=business.id,
        customer_id=customers[0].id,
        order_number="ORD-20250220-002",
        status="pending",
        subtotal=165.00,
        delivery_fee=30,
        total=195.00,
        payment_method="cod",
        delivery_address=customers[0].addresses[0],
        created_at=datetime.utcnow() - timedelta(minutes=10)
    )
    db.add(order3)
    db.flush()
    
    order3_items = [
        StoreOrderItem(
            order_id=order3.id,
            product_id=products[3].id,
            product_name="Rice Flour",
            quantity=1,
            unit_price=40.00,
            total_price=40.00
        ),
        StoreOrderItem(
            order_id=order3.id,
            product_id=products[6].id,
            product_name="Rice Flakes (Poha)",
            quantity=1,
            unit_price=125.00,
            total_price=125.00
        )
    ]
    for item in order3_items:
        db.add(item)
    
    print(f"✅ Created 3 sample orders")
    
    # ═══════════════════════════════════════════════════════════════════
    # 6. COMMIT EVERYTHING
    # ═══════════════════════════════════════════════════════════════════
    
    db.commit()
    db.refresh(business)
    
    print(f"\n🎉 Demo store '{business.name}' created successfully!")
    print(f"   Storefront URL: /store/{business.slug}")
    print(f"   Products: {len(products)}")
    print(f"   Customers: {len(customers)}")
    print(f"   Orders: 3")
    print(f"\n✅ Ready to test!")
    
    return business


if __name__ == "__main__":
    from database.db import get_db_session
    
    print("🧪 Testing Demo Data Generator...")
    db = get_db_session()
    business = create_demo_store(db, user_id=1)
    print(f"\n✅ Success! Visit: http://localhost:8000/store/{business.slug}")