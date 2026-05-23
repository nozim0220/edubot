"""Faxrli yorliq (certificate) generatsiya."""
import io
import os
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


GRADE_LABELS = {
    (0, 40):  ("🔴", "Boshlang'ich",  "Davom eting!"),
    (40, 60): ("🟡", "O'rta daraja",  "Yaxshi natija!"),
    (60, 75): ("🟢", "Yaxshi",        "Zo'r ish!"),
    (75, 90): ("💎", "A'lo",          "Ajoyib natija!"),
    (90,101): ("🏆", "Mukammal",      "Tengsiz natija!"),
}


def get_grade(score: int) -> tuple:
    """Ball bo'yicha daraja."""
    for (lo, hi), info in GRADE_LABELS.items():
        if lo <= score < hi:
            return info
    return ("🏆", "Mukammal", "Tengsiz natija!")


def generate_certificate_text(
    user_name: str,
    exam_name: str,
    score: int,
    correct: int,
    total: int,
    date_str: str,
    cert_id: str,
) -> str:
    """Matnli sertifikat generatsiya."""
    emoji, grade_name, slogan = get_grade(score)

    stars = "⭐" * min(5, max(1, score // 20))

    text = (
        f"╔══════════════════════════════╗\n"
        f"║     🎓 FAXRLI YORLIQ 🎓      ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"👤 <b>{user_name}</b>\n\n"
        f"📝 Imtihon: <b>{exam_name}</b>\n"
        f"📊 Natija: <b>{correct}/{total} ({score}%)</b>\n"
        f"{emoji} Daraja: <b>{grade_name}</b>\n"
        f"{stars}\n\n"
        f"💬 {slogan}\n\n"
        f"📅 Sana: {date_str}\n"
        f"🔐 ID: <code>{cert_id}</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 ABT Yordamchi Bot"
    )
    return text


def generate_certificate_image(
    user_name: str,
    exam_name: str,
    score: int,
    correct: int,
    total: int,
    date_str: str,
    cert_id: str,
) -> io.BytesIO | None:
    """Rasmli sertifikat (PIL mavjud bo'lsa)."""
    if not PIL_AVAILABLE:
        return None

    try:
        W, H = 800, 560
        img = Image.new('RGB', (W, H), color='#0a0e1a')
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(H):
            ratio = y / H
            r = int(10 + 20 * ratio)
            g = int(14 + 30 * ratio)
            b = int(26 + 40 * ratio)
            draw.line([(0, y), (W, y)], fill=(r, g, b))

        # Border
        draw.rectangle([10, 10, W-10, H-10], outline='#ffd700', width=3)
        draw.rectangle([20, 20, W-20, H-20], outline='#ffd700', width=1)

        # Stars corner decorations
        for pos in [(40, 40), (W-60, 40), (40, H-60), (W-60, H-60)]:
            draw.text(pos, "★", fill='#ffd700')

        emoji_map = {(0,40):"🔴",(40,60):"🟡",(60,75):"🟢",(75,90):"💎",(90,101):"🏆"}
        grade_emoji = "🏆"
        grade_name  = "Mukammal"
        for (lo, hi), (em, gn, _) in GRADE_LABELS.items():
            if lo <= score < hi:
                grade_emoji = em; grade_name = gn; break

        # Fonts — fallback to default
        try:
            BASE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            font_path = os.path.join(BASE, 'static', 'fonts', 'DejaVuSans.ttf')
            font_big   = ImageFont.truetype(font_path, 36)
            font_med   = ImageFont.truetype(font_path, 24)
            font_small = ImageFont.truetype(font_path, 18)
        except Exception:
            font_big   = ImageFont.load_default()
            font_med   = font_big
            font_small = font_big

        def center_text(text, y, font, color='white'):
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            draw.text(((W - w) // 2, y), text, fill=color, font=font)

        center_text("FAXRLI YORLIQ", 50,  font_big,   '#ffd700')
        center_text("Certificate of Achievement", 100, font_small, '#aaaaaa')

        draw.line([(60, 130), (W-60, 130)], fill='#ffd700', width=1)

        center_text(user_name,   160, font_med,   '#ffffff')
        center_text(exam_name,   210, font_small, '#aaccff')
        center_text(f"{correct}/{total} savol — {score}%", 255, font_big, '#00ff88')

        stars_txt = "★" * min(5, max(1, score // 20))
        center_text(stars_txt,   315, font_med, '#ffd700')
        center_text(grade_name,  355, font_med, '#ffd700')

        draw.line([(60, 395), (W-60, 395)], fill='#444444', width=1)

        center_text(f"Sana: {date_str}",     415, font_small, '#888888')
        center_text(f"ID: {cert_id}",        445, font_small, '#555555')
        center_text("🤖 ABT Yordamchi Bot",  490, font_small, '#ffd700')

        buf = io.BytesIO()
        img.save(buf, format='PNG', quality=95)
        buf.seek(0)
        return buf
    except Exception as e:
        return None
