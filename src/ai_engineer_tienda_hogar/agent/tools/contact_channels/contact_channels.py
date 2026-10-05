import re
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


EMAIL_RE = r"[\w\.-]+@[\w\.-]+\.\w+"
PHONE_RE = r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{4}"
WHATSAPP_RE = r"(?:https?://)?(?:wa\.me/\d+|api\.whatsapp\.com/send\?phone=\+?\d+|\+?\d{7,15})"
TELEGRAM_RE = r"(?:https?://)?(?:t\.me/[A-Za-z0-9_]+|@[A-Za-z0-9_]+)"


def _find_first(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


@tool
def extract_contact_channels(file_path: str) -> dict:
    """Extract official contact channels from the contact channels document."""
    content = Path(file_path).read_text(encoding="utf-8")

    return {
        "email": _find_first(EMAIL_RE, content),
        "phone": _find_first(PHONE_RE, content),
        "whatsapp": _find_first(WHATSAPP_RE, content),
        "telegram": _find_first(TELEGRAM_RE, content),
    }