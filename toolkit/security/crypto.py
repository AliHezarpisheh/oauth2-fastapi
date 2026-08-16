"""Module defining components for cryptographic and secrets-related operations."""

import hashlib
import secrets


def generate_secret(nbytes: int = 32) -> str:
    """Generate cryptographically secure, random text string that is safe to urls."""
    return secrets.token_urlsafe(nbytes)


def generate_text_hash(text: str) -> str:
    """Generate hash values for texts that are random and not human-chosen."""
    return hashlib.sha512(text.encode()).hexdigest()
