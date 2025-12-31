"""Password hashing utilities using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: bcrypt hash (60 characters, format: $2b$12$...)
    
    Example:
        >>> hashed = hash_password("SecurePassword123")
        >>> hashed.startswith("$2b$")
        True
    """
    # Trim password (remove leading/trailing whitespace)
    password = password.strip()
    
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash (12 rounds = cost factor)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: bcrypt hash to verify against
    
    Returns:
        bool: True if password matches, False otherwise
    
    Example:
        >>> hashed = hash_password("SecurePassword123")
        >>> verify_password("SecurePassword123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    # Trim password before verification
    plain_password = plain_password.strip()
    
    # Encode both password and hash to bytes
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    # Verify using bcrypt
    return bcrypt.checkpw(password_bytes, hash_bytes)

