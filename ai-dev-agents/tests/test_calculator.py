"""
Comprehensive unit tests for calculator module
"""

import pytest
from src.calculator import add, divide, calculate_discount


class TestAdd:
    """Test cases for the add function"""

    def test_add_positive_numbers(self):
        """Test adding two positive numbers"""
        assert add(2, 3) == 5
        assert add(10.5, 3.2) == 13.7

    def test_add_negative_numbers(self):
        """Test adding two negative numbers"""
        assert add(-2, -3) == -5
        assert add(-10.5, -3.2) == -13.7

    def test_add_positive_and_negative(self):
        """Test adding positive and negative numbers"""
        assert add(5, -3) == 2
        assert add(-8, 12) == 4
        assert add(10.5, -10.5) == 0

    def test_add_zero_values(self):
        """Test adding zero values"""
        assert add(0, 0) == 0
        assert add(5, 0) == 5
        assert add(0, -3) == -3

    def test_add_large_numbers(self):
        """Test adding large numbers"""
        assert add(1e6, 2e6) == 3e6
        assert add(float('inf'), 5) == float('inf')

    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (0, 0, 0),
        (-1, -1, -2),
        (3.14, 2.86, 6.0),
        (100, -50, 50),
    ])
    def test_add_parametrized(self, a, b, expected):
        """Parametrized tests for add function"""
        assert add(a, b) == pytest.approx(expected, rel=1e-9)


class TestDivide:
    """Test cases for the divide function"""

    def test_divide_positive_numbers(self):
        """Test dividing positive numbers"""
        assert divide(10, 2) == 5
        assert divide(15.6, 3.2) == pytest.approx(4.875, rel=1e-9)

    def test_divide_negative_numbers(self):
        """Test dividing with negative numbers"""
        assert divide(-10, 2) == -5
        assert divide(10, -2) == -5
        assert divide(-10, -2) == 5

    def test_divide_by_zero_raises_error(self):
        """Test that dividing by zero raises ValueError"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(-5, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(0, 0)

    def test_divide_zero_by_number(self):
        """Test dividing zero by a non-zero number"""
        assert divide(0, 5) == 0
        assert divide(0, -3) == 0
        assert divide(0, 0.1) == 0

    def test_divide_decimal_results(self):
        """Test division that results in decimal values"""
        assert divide(1, 3) == pytest.approx(0.33333333333, rel=1e-9)
        assert divide(7, 2) == 3.5
        assert divide(22, 7) == pytest.approx(3.142857142857, rel=1e-9)

    def test_divide_large_numbers(self):
        """Test dividing large numbers"""
        assert divide(1e6, 1e3) == 1e3
        assert divide(float('inf'), 2) == float('inf')

    @pytest.mark.parametrize("a,b,expected", [
        (10, 2, 5),
        (100, 10, 10),
        (-20, 4, -5),
        (15, -3, -5),
        (-12, -4, 3),
        (7.5, 2.5, 3),
    ])
    def test_divide_parametrized(self, a, b, expected):
        """Parametrized tests for divide function"""
        assert divide(a, b) == pytest.approx(expected, rel=1e-9)


class TestCalculateDiscount:
    """Test cases for the calculate_discount function"""

    def test_calculate_discount_valid_inputs(self):
        """Test calculate_discount with valid inputs"""
        assert calculate_discount(100, 10) == 90
        assert calculate_discount(50, 20) == 40
        assert calculate_discount(200, 50) == 100

    def test_calculate_discount_zero_discount(self):
        """Test calculate_discount with zero discount"""
        assert calculate_discount(100, 0) == 100
        assert calculate_discount(50.5, 0) == 50.5

    def test_calculate_discount_hundred_percent_discount(self):
        """Test calculate_discount with 100% discount"""
        assert calculate_discount(100, 100) == 0
        assert calculate_discount(75.25, 100) == 0

    def test_calculate_discount_zero_price(self):
        """Test calculate_discount with zero price"""
        assert calculate_discount(0, 10) == 0
        assert calculate_discount(0, 50) == 0
        assert calculate_discount(0, 100) == 0

    def test_calculate_discount_decimal_values(self):
        """Test calculate_discount with decimal values"""
        assert calculate_discount(99.99, 25) == pytest.approx(74.9925, rel=1e-9)
        assert calculate_discount(123.45, 15.5) == pytest.approx(104.33475, rel=1e-9)

    def test_calculate_discount_negative_price_raises_error(self):
        """Test that negative price raises ValueError"""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            calculate_discount(-10, 10)
        
        with pytest.raises(ValueError, match="Price cannot be negative"):
            calculate_discount(-0.01, 5)

    def test_calculate_discount_invalid_discount_percent_raises_error(self):
        """Test that invalid discount percentages raise ValueError"""
        # Negative discount
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            calculate_discount(100, -1)
        
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            calculate_discount(50, -10)
        
        # Discount over 100%
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            calculate_discount(100, 101)
        
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            calculate_discount(50, 150)

    def test_calculate_discount_boundary_values(self):
        """Test calculate_discount with boundary values"""
        # Minimum valid discount (0%)
        assert calculate_discount(100, 0) == 100
        # Maximum valid discount (100%)
        assert calculate_discount(100, 100) == 0
        # Very small price
        assert calculate_discount(0.01, 50) == pytest.approx(0.005, rel=1e-9)
        # Large price
        assert calculate_discount(10000, 25) == 7500

    @pytest.mark.parametrize("price,discount,expected", [
        (100, 10, 90),
        (200, 25, 150),
        (50, 50, 25),
        (75.5, 20, 60.4),
        (1000, 15, 850),
        (99.99, 33.33, 66.6566670000),
    ])
    def test_calculate_discount_parametrized(self, price, discount, expected):
        """Parametrized tests for calculate_discount function"""
        assert calculate_discount(price, discount) == pytest.approx(expected, rel=1e-7)

    def test_calculate_discount_edge_cases(self):
        """Test calculate_discount edge cases"""
        # Very small discount
        assert calculate_discount(100, 0.01) == pytest.approx(99.99, rel=1e-9)
        # Very large price with small discount
        assert calculate_discount(1e6, 1) == pytest.approx(990000, rel=1e-9)
        # Fractional discount percentages
        assert calculate_discount(100, 12.5) == 87.5
        assert calculate_discount(80, 37.5) == 50