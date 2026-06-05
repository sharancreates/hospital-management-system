import pytest
from datetime import date
from routes.utils import (
    validate_email,
    validate_phone,
    validate_age,
    validate_date,
    sanitize_string,
    validate_password_complexity
)

def test_validate_email():
    # Valid emails
    assert validate_email("test@example.com") == "test@example.com"
    assert validate_email("   user.name+label@sub.domain.org  ") == "user.name+label@sub.domain.org"
    
    # Invalid emails
    with pytest.raises(ValueError, match="Invalid email format"):
        validate_email("invalid-email")
    with pytest.raises(ValueError, match="Invalid email format"):
        validate_email("test@domain")
    with pytest.raises(ValueError, match="Invalid email field"):
        validate_email(None)

def test_validate_phone():
    # Valid phone formats
    assert validate_phone("1234567890") == "1234567890"
    assert validate_phone("  +91 98765-43210 ") == "+919876543210"
    
    # Invalid phone formats
    with pytest.raises(ValueError, match="Contact number must be between 10 and 15 digits"):
        validate_phone("12345")
    with pytest.raises(ValueError, match="Contact number must be between 10 and 15 digits"):
        validate_phone("1234567890123456")
    with pytest.raises(ValueError, match="Contact number is required"):
        validate_phone(None)

def test_validate_age():
    # Valid ages
    assert validate_age(25) == 25
    assert validate_age("99") == 99
    
    # Invalid ages
    with pytest.raises(ValueError, match="Age must be a positive number"):
        validate_age(0)
    with pytest.raises(ValueError, match="Age must be a positive number"):
        validate_age(-5)
    with pytest.raises(ValueError, match="Age must be a positive number"):
        validate_age(150)
    with pytest.raises(ValueError, match="Age must be a positive number"):
        validate_age("not-a-number")

def test_validate_date():
    # Valid date
    assert validate_date("2026-06-04") == date(2026, 6, 4)
    
    # Invalid date formats
    with pytest.raises(ValueError, match="must be in YYYY-MM-DD format"):
        validate_date("04-06-2026")
    with pytest.raises(ValueError, match="must be in YYYY-MM-DD format"):
        validate_date("2026/06/04")
    with pytest.raises(ValueError, match="is required"):
        validate_date(None)

def test_sanitize_string():
    # Valid strings
    assert sanitize_string("hello") == "hello"
    assert sanitize_string("  trimmed  ") == "trimmed"
    
    # Escapes HTML entities
    assert sanitize_string("<html>test</html>") == "&lt;html&gt;test&lt;/html&gt;"
    
    # Empty string behavior
    assert sanitize_string("", min_len=0) == ""
    with pytest.raises(ValueError, match="Text is required"):
        sanitize_string("")
        
    # Bounds checks
    with pytest.raises(ValueError, match="is too short"):
        sanitize_string("a", min_len=3)
    with pytest.raises(ValueError, match="exceeds max length"):
        sanitize_string("abc", max_len=2)

def test_validate_password_complexity():
    # Valid password
    ok, msg = validate_password_complexity("StrongPass123!")
    assert ok
    assert msg == ""
    
    # Missing parameters
    ok, msg = validate_password_complexity("short")
    assert not ok
    assert "at least 8 characters" in msg
    
    ok, msg = validate_password_complexity("NOLOWERCASE1!")
    assert not ok
    assert "lowercase letter" in msg
    
    ok, msg = validate_password_complexity("nouppercase1!")
    assert not ok
    assert "uppercase letter" in msg
    
    ok, msg = validate_password_complexity("NoDigits!!")
    assert not ok
    assert "digit" in msg
    
    ok, msg = validate_password_complexity("NoSpecial123")
    assert not ok
    assert "special character" in msg
