# ═══════════════════════════════════════════════════════════════════
# AI HELPERS - Food Ordering Store
# ═══════════════════════════════════════════════════════════════════
#
# Save this as: utils/ai_helpers.py
#
# AI-powered features using Ollama (your existing setup)
#
# ═══════════════════════════════════════════════════════════════════

import ollama
import json
from typing import List, Dict, Optional
from database.crud_store import list_products, get_customer_by_phone


# ═══════════════════════════════════════════════════════════════════
# CHAT ORDERING - Main AI Function
# ═══════════════════════════════════════════════════════════════════

async def chat_with_customer(
    message: str,
    business_id: int,
    db,
    context: dict = None
) -> dict:
    """
    Handle customer chat message and return intelligent response
    
    Args:
        message: Customer's message
        business_id: Which business they're ordering from
        db: Database session
        context: Previous conversation context
        
    Returns:
        dict: {
            "response": "text to show customer",
            "suggested_products": [list of product dicts],
            "action": "show_products|add_to_cart|clarify|checkout",
            "intent": "browse|order|question|chitchat"
        }
    """
    
    # Get all products for this business
    products = list_products(db, business_id, active_only=True, in_stock_only=True)
    
    # Build product catalog for AI
    product_catalog = "\n".join([
        f"- {p.name}: ₹{p.price} ({p.unit}) - {p.description[:100]}..."
        for p in products
    ])
    
    # Build conversation history if available
    conversation_history = ""
    if context and context.get("previous_messages"):
        conversation_history = "Previous conversation:\n"
        for msg in context["previous_messages"][-3:]:  # Last 3 messages
            conversation_history += f"{msg['role']}: {msg['content']}\n"
    
    # Current cart context
    cart_info = ""
    if context and context.get("cart"):
        cart_items = context["cart"]
        if cart_items:
            cart_info = f"\nCustomer's current cart: {len(cart_items)} items\n"
            for item in cart_items:
                cart_info += f"- {item['name']} x{item['quantity']}\n"
    
    # Build prompt for AI
    prompt = f"""You are a helpful, friendly food ordering assistant for a South Indian food business.

Available Products:
{product_catalog}

{conversation_history}
{cart_info}

Customer just said: "{message}"

Your task:
1. Understand what the customer wants
2. Suggest relevant products naturally
3. Be conversational and warm (like talking to Amma!)
4. If they mention quantity/people, adjust recommendations
5. Guide them toward placing an order

Respond in JSON format:
{{
    "response": "your friendly message to customer",
    "suggested_products": [
        {{"product_name": "exact product name", "quantity": 1, "reason": "why this fits their need"}}
    ],
    "action": "show_products|add_to_cart|clarify|checkout|chitchat",
    "intent": "browse|order|question|chitchat"
}}

Examples:

Customer: "breakfast"
Response: {{
    "response": "Great choice! For how many people are you planning breakfast?",
    "suggested_products": [
        {{"product_name": "IDLI/DOSA Batter", "quantity": 1, "reason": "most popular breakfast item"}}
    ],
    "action": "clarify",
    "intent": "browse"
}}

Customer: "for 2 people"
Response: {{
    "response": "Perfect! One batch of IDLI/DOSA Batter makes about 20 idlis - plenty for 2 people! Want to add coconut chutney to go with it?",
    "suggested_products": [
        {{"product_name": "IDLI/DOSA Batter", "quantity": 1, "reason": "makes 20 idlis, enough for 2"}},
        {{"product_name": "Rice Flour", "quantity": 1, "reason": "can make chutney powder"}}
    ],
    "action": "show_products",
    "intent": "order"
}}

Customer: "yes add both"
Response: {{
    "response": "Wonderful! I've added IDLI/DOSA Batter and Rice Flour to your cart. Anything else you need today?",
    "suggested_products": [],
    "action": "add_to_cart",
    "intent": "order"
}}

Customer: "that's all"
Response: {{
    "response": "Perfect! Ready to place your order? I'll need your phone number and delivery address.",
    "suggested_products": [],
    "action": "checkout",
    "intent": "order"
}}

Now respond to: "{message}"
"""
    
    try:
        # Call Ollama AI (using your existing setup)
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": prompt}],
            format="json"  # Force JSON output
        )
        
        result = json.loads(response["message"]["content"])
        
        # Match suggested products to actual product IDs
        if result.get("suggested_products"):
            matched_products = []
            for suggestion in result["suggested_products"]:
                # Find matching product
                for product in products:
                    if product.name.lower() == suggestion["product_name"].lower():
                        matched_products.append({
                            "id": product.id,
                            "name": product.name,
                            "price": product.price,
                            "unit": product.unit,
                            "image_url": product.image_url,
                            "quantity": suggestion.get("quantity", 1),
                            "reason": suggestion.get("reason", "")
                        })
                        break
            result["suggested_products"] = matched_products
        
        return result
        
    except Exception as e:
        print(f"AI Error: {e}")
        # Fallback response
        return {
            "response": "I'm here to help you order! What would you like today?",
            "suggested_products": [],
            "action": "clarify",
            "intent": "browse"
        }


# ═══════════════════════════════════════════════════════════════════
# PRODUCT DESCRIPTION GENERATOR
# ═══════════════════════════════════════════════════════════════════

async def generate_product_description(
    product_name: str,
    category: str,
    price: float,
    unit: str = None
) -> str:
    """
    Generate appealing product description using AI
    
    Args:
        product_name: Name of the product
        category: Category (Batters, Flours, etc.)
        price: Price in rupees
        unit: Unit (1/2 kg, 500g, etc.)
        
    Returns:
        str: Generated description
    """
    
    prompt = f"""Write an appetizing, concise product description for a South Indian food item.

Product: {product_name}
Category: {category}
Price: ₹{price}
Unit: {unit or ""}

Requirements:
- 2-3 sentences maximum
- Highlight freshness, quality, taste
- Mention use cases
- Make it sound delicious but authentic
- Professional but warm tone (like Amma describing her cooking)
- Don't use superlatives too much

Example for "IDLI Batter":
"Fresh homemade idli batter made with organic rice and urad dal. Perfectly fermented for soft idlis and crispy dosas. Makes approximately 20 idlis."

Example for "Wheat Flour":
"Stone-ground whole wheat flour from local farms. Perfect for chapatis, parathas, and baking. Freshly ground every week to preserve nutrients."

Now write for "{product_name}" in {category} category:"""
    
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        
        description = response["message"]["content"].strip()
        # Remove quotes if AI added them
        description = description.strip('"').strip("'")
        
        return description
        
    except Exception as e:
        print(f"AI Error generating description: {e}")
        # Fallback generic description
        return f"Fresh {product_name.lower()} available now. Perfect for your daily needs."


# ═══════════════════════════════════════════════════════════════════
# COMPLEMENTARY PRODUCT SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════

async def suggest_complementary_products(
    cart_items: List[dict],
    all_products: List,
    max_suggestions: int = 3
) -> List[dict]:
    """
    Suggest products that go well with items in cart
    
    Args:
        cart_items: List of items currently in cart
        all_products: All available products
        max_suggestions: Max number of suggestions
        
    Returns:
        List of suggested products with reasons
    """
    
    if not cart_items:
        return []
    
    # Build cart summary
    cart_summary = ", ".join([item["name"] for item in cart_items])
    
    # Build available products list
    available = "\n".join([
        f"- {p.name} (₹{p.price})"
        for p in all_products
        if p.name not in [item["name"] for item in cart_items]  # Exclude already in cart
    ])
    
    prompt = f"""You're helping a customer complete their food order.

They currently have in cart:
{cart_summary}

Available products:
{available}

Suggest {max_suggestions} complementary products that would go well with their order.
Be specific about WHY they go together.

Think about:
- Traditional pairings (idli + chutney, dosa + sambhar)
- Balanced meals (carbs + proteins)
- Convenience (if buying batter, maybe also need flour for something else)

Respond in JSON:
{{
    "suggestions": [
        {{"product": "exact product name", "reason": "specific reason why this pairs well"}}
    ]
}}

Examples:

Cart: ["IDLI/DOSA Batter"]
Suggestions: [
    {{"product": "Rice Flour", "reason": "Make coconut chutney powder to pair with idlis"}},
    {{"product": "Wheat Flakes (Aval)", "reason": "Quick breakfast alternative for variety"}}
]

Cart: ["Wheat Flour (Atta)"]
Suggestions: [
    {{"product": "Rice Flakes (Poha)", "reason": "Healthy breakfast option alongside chapatis"}},
    {{"product": "Murukku Mix", "reason": "Tea-time snack to complement your meals"}}
]

Now suggest for cart: [{cart_summary}]
"""
    
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        
        result = json.loads(response["message"]["content"])
        suggestions = []
        
        # Match to actual products
        for suggestion in result.get("suggestions", [])[:max_suggestions]:
            for product in all_products:
                if product.name.lower() == suggestion["product"].lower():
                    suggestions.append({
                        "id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "unit": product.unit,
                        "image_url": product.image_url,
                        "reason": suggestion["reason"]
                    })
                    break
        
        return suggestions
        
    except Exception as e:
        print(f"AI Error suggesting products: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════
# PARSE ORDER FROM NATURAL LANGUAGE
# ═══════════════════════════════════════════════════════════════════

async def parse_order_from_text(
    text: str,
    business_id: int,
    db
) -> dict:
    """
    Extract order details from unstructured text
    Useful for manual order entry or WhatsApp messages
    
    Args:
        text: Unstructured order text
        business_id: Business ID
        db: Database session
        
    Returns:
        dict: Parsed order with items
    """
    
    products = list_products(db, business_id, active_only=True)
    
    product_list = "\n".join([
        f"- {p.name}: ₹{p.price} ({p.unit})"
        for p in products
    ])
    
    prompt = f"""Extract order details from this message.

Available Products:
{product_list}

Customer Message:
"{text}"

Extract:
- Which products they want
- Quantities
- Any special instructions

Respond in JSON:
{{
    "items": [
        {{"product_name": "exact product name", "quantity": 1, "notes": "any special request"}}
    ],
    "customer_name": "name if mentioned",
    "phone": "phone if mentioned",
    "address": "address if mentioned",
    "delivery_instructions": "any delivery notes"
}}

Examples:

Message: "I want 2 idli batter and 1 wheat flakes. Ramesh. 9876543210"
Response: {{
    "items": [
        {{"product_name": "IDLI/DOSA Batter", "quantity": 2, "notes": null}},
        {{"product_name": "Wheat Flakes (Aval)", "quantity": 1, "notes": null}}
    ],
    "customer_name": "Ramesh",
    "phone": "9876543210",
    "address": null,
    "delivery_instructions": null
}}

Now parse: "{text}"
"""
    
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        
        result = json.loads(response["message"]["content"])
        
        # Match products to IDs
        if result.get("items"):
            matched_items = []
            for item in result["items"]:
                for product in products:
                    if product.name.lower() == item["product_name"].lower():
                        matched_items.append({
                            "product_id": product.id,
                            "product_name": product.name,
                            "quantity": item["quantity"],
                            "unit_price": product.price,
                            "notes": item.get("notes")
                        })
                        break
            result["items"] = matched_items
        
        return result
        
    except Exception as e:
        print(f"AI Error parsing order: {e}")
        return {"items": [], "error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# CUSTOMER INSIGHTS
# ═══════════════════════════════════════════════════════════════════

async def analyze_customer_preferences(
    customer_phone: str,
    business_id: int,
    db
) -> dict:
    """
    Analyze customer's past orders to personalize experience
    
    Returns preferences, favorites, patterns
    """
    
    customer = get_customer_by_phone(db, business_id, customer_phone)
    
    if not customer or not customer.orders:
        return {
            "is_new": True,
            "greeting": "Welcome! First time ordering with us?",
            "favorites": [],
            "suggestions": []
        }
    
    # Get order history
    orders = customer.orders[:10]  # Last 10 orders
    
    order_summary = []
    for order in orders:
        items = [f"{item.product_name} x{item.quantity}" for item in order.items]
        order_summary.append({
            "date": order.created_at.strftime("%Y-%m-%d"),
            "items": items,
            "total": order.total
        })
    
    prompt = f"""Analyze this customer's ordering patterns:

Customer: {customer.name}
Total Orders: {customer.total_orders}
Total Spent: ₹{customer.total_spent}

Recent Orders:
{json.dumps(order_summary, indent=2)}

Identify:
1. Favorite products (ordered most often)
2. Ordering frequency
3. Average order value
4. Any patterns (regular items, specific day preferences)

Respond in JSON:
{{
    "favorites": ["product1", "product2"],
    "frequency": "weekly|biweekly|monthly",
    "avg_order_value": 200,
    "is_regular": true,
    "personalized_greeting": "warm, short greeting for returning customer",
    "quick_reorder_suggestion": "suggest their usual order"
}}
"""
    
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        
        result = json.loads(response["message"]["content"])
        result["is_new"] = False
        
        return result
        
    except Exception as e:
        print(f"AI Error analyzing customer: {e}")
        return {
            "is_new": False,
            "greeting": f"Welcome back, {customer.name}!",
            "favorites": [],
            "is_regular": customer.is_regular
        }


# ═══════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio
    
    async def test_ai():
        print("🧪 Testing AI Helpers...")
        
        # Test product description
        desc = await generate_product_description(
            "IDLI/DOSA Batter",
            "Batters",
            50.0,
            "1/2 kg"
        )
        print(f"\nGenerated Description:\n{desc}")
        
        # Test complementary suggestions
        cart = [{"name": "IDLI/DOSA Batter"}]
        # suggestions = await suggest_complementary_products(cart, [])
        # print(f"\nSuggestions: {suggestions}")
    
    asyncio.run(test_ai())
