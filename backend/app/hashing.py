import hashlib
import re

from app.config import settings


def hash_nhs_number(nhs_number: str) -> str:
    """Hash NHS number using SHA-256 + secret salt."""
    cleaned = re.sub(r"[\s\-]", "", nhs_number)
    if not re.match(r"^\d{10}$", cleaned):
        raise ValueError("NHS number must be exactly 10 digits")

    salted = f"{cleaned}{settings.SECRET_SALT}"
    return hashlib.sha256(salted.encode()).hexdigest()


def generate_pseudonym(sequence: int) -> str:
    """Generate pseudonym in format PAT-XXXXXX."""
    return f"PAT-{sequence:06d}"


def validate_nhs_number(nhs_number: str) -> bool:
    """Validate NHS number format (basic check only)."""
    cleaned = re.sub(r"[\s\-]", "", nhs_number)
    return bool(re.match(r"^\d{10}$", cleaned))
