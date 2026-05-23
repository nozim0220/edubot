"""Utility helpers for the bot."""
from typing import Optional
from aiogram.types import Message, CallbackQuery


def get_user_id(event) -> Optional[int]:
    """Extract user Telegram ID from event."""
    if isinstance(event, Message):
        return event.from_user.id if event.from_user else None
    if isinstance(event, CallbackQuery):
        return event.from_user.id if event.from_user else None
    return None


def format_number(num: int) -> str:
    """Format number with thousands separators."""
    return f"{num:,}".replace(',', ' ')


def format_usd(amount) -> str:
    """Format USD amount."""
    if amount is None:
        return "N/A"
    return f"${float(amount):,.0f}"


def format_uzs(amount) -> str:
    """Format UZS amount."""
    if amount is None:
        return "N/A"
    return f"{int(float(amount)):,} so'm".replace(',', ' ')


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    return text[:max_len] + ("..." if len(text) > max_len else "")


def get_flag(country_code: str) -> str:
    """Get flag emoji for country code."""
    flags = {
        'UZ': '🇺🇿', 'US': '🇺🇸', 'GB': '🇬🇧', 'DE': '🇩🇪',
        'RU': '🇷🇺', 'KR': '🇰🇷', 'TR': '🇹🇷', 'CN': '🇨🇳',
        'JP': '🇯🇵', 'MY': '🇲🇾', 'FR': '🇫🇷', 'IT': '🇮🇹',
        'CA': '🇨🇦', 'AU': '🇦🇺', 'NL': '🇳🇱', 'SE': '🇸🇪',
    }
    return flags.get(country_code, '🌍')


def level_progress_bar(current_xp: int, next_level_xp: int, prev_level_xp: int = 0, length: int = 10) -> str:
    """Generate ASCII progress bar for XP level."""
    total = next_level_xp - prev_level_xp
    earned = current_xp - prev_level_xp
    if total <= 0:
        filled = length
    else:
        filled = int((earned / total) * length)
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    pct = int((earned / total * 100)) if total > 0 else 100
    return f"[{bar}] {pct}%"


def split_message(text: str, max_len: int = 4000) -> list:
    """Split long message into chunks."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind('\n', 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip('\n')
    return chunks
