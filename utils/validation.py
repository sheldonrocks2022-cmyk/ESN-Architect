"""Shared validation and safety helpers for ESN Forge."""
import re
from urllib.parse import urlparse

HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def parse_hex_color(value: str) -> int:
    if not HEX_RE.fullmatch(value.strip()):
        raise ValueError("Color must be a 6-digit hexadecimal value.")
    return int(value.strip().lstrip("#"), 16)


def safe_slug(value: str, fallback: str = "forge-project", limit: int = 48) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-_").lower()
    return (value[:limit] or fallback)


def valid_http_url(value: str) -> bool:
    if not value:
        return True
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def clean_csv(value: str, limit: int = 20) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()][:limit]
