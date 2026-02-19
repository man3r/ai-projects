"""
Sample calculator module for testing the Unit Test Agent
"""


def add(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide a by b
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate final price after applying a discount percentage
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
        
    Returns:
        Final price after discount
        
    Raises:
        ValueError: If price is negative or discount is not between 0-100
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100")
    return price * (1 - discount_percent / 100)


def is_even(number: int) -> bool:
    """Check if a number is even"""
    return number % 2 == 0
