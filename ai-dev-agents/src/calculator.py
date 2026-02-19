"""
Simple calculator functions for demonstration
"""

def add(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate price after applying discount percentage"""
    if price < 0:
        raise ValueError("Price cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100")
    return price * (1 - discount_percent / 100)
