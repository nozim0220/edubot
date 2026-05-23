"""Faxr yorliq (sertifikat) generatsiyasi — matn ko'rinishida."""

CERT_TEMPLATES = {
    "excellent": {
        "emoji": "🏆",
        "title": "A'LO NATIJA",
        "color": "oltin",
    },
    "good": {
        "emoji": "🥈",
        "title": "YAXSHI NATIJA",
        "color": "kumush",
    },
    "pass": {
        "emoji": "🥉",
        "title": "MUVAFFAQIYATLI",
        "color": "bronza",
    },
}

SUBJECT_FULL = {
    "ielts":    "IELTS",
    "sat":      "SAT",
    "math":     "Matematika",
    "physics":  "Fizika",
    "chemistry":"Kimyo",
    "biology":  "Biologiya",
    "history":  "Tarix",
    "it":       "Informatika",
}


def generate_certificate_text(
    user_name: str,
    subject_key: str,
    score_pct: int,
    correct: int,
    total: int,
    extra_score: str = "",
    cert_id: str = "",
) -> str:
    """Mock imtihon sertifikat matni."""
    if score_pct >= 80:
        tmpl = CERT_TEMPLATES["excellent"]
    elif score_pct >= 60:
        tmpl = CERT_TEMPLATES["good"]
    else:
        tmpl = CERT_TEMPLATES["pass"]

    subject = SUBJECT_FULL.get(subject_key, subject_key.upper())
    from datetime import date
    today = date.today().strftime("%d.%m.%Y")

    cert_text = (
        f"{'─'*32}\n"
        f"{tmpl['emoji']}  <b>FAXR YORLIQI</b>  {tmpl['emoji']}\n"
        f"{'─'*32}\n\n"
        f"👤 <b>{user_name}</b>\n\n"
        f"📚 Fan: <b>{subject}</b>\n"
        f"📊 Natija: <b>{correct}/{total}</b> ({score_pct}%)\n"
    )
    if extra_score:
        cert_text += f"🎯 {extra_score}\n"
    cert_text += (
        f"🏅 Daraja: <b>{tmpl['title']}</b>\n\n"
        f"📅 Sana: {today}\n"
        f"🔖 ID: <code>{cert_id}</code>\n\n"
        f"{'─'*32}\n"
        f"✅ <i>EduBot tomonidan berildi</i>"
    )
    return cert_text


def get_university_recommendations(subject_key: str, score_pct: int,
                                    ielts_band: float = None, sat_score: int = None,
                                    dtm_score: int = None) -> list:
    """Ball asosida universitet tavsiyalari."""
    recommendations = []

    if subject_key in ("ielts", "sat") or ielts_band or sat_score:
        # Xalqaro universitetlar
        if score_pct >= 85:
            recommendations = [
                {"name": "MIT", "country": "🇺🇸", "chance": "Yuqori", "emoji": "🟢",
                 "note": f"Sizning IELTS {ielts_band or '?'} yetarli"},
                {"name": "University of Oxford", "country": "🇬🇧", "chance": "O'rta-Yuqori", "emoji": "🟡",
                 "note": "IELTS 7.5 talab qiladi"},
                {"name": "Technical University Munich", "country": "🇩🇪", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Bepul ta'lim, IELTS 6.5+"},
                {"name": "Seoul National Univ.", "country": "🇰🇷", "chance": "Yuqori", "emoji": "🟢",
                 "note": "GKS stipendiyasi bor"},
            ]
        elif score_pct >= 65:
            recommendations = [
                {"name": "METU (Turkiya)", "country": "🇹🇷", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Turkiya Burslari stipendiyasi"},
                {"name": "WIUT (Toshkent)", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Ingliz tilida, IELTS 5.5+"},
                {"name": "Univ. of Malaya", "country": "🇲🇾", "chance": "O'rta", "emoji": "🟡",
                 "note": "Arzon, IELTS 6.0"},
                {"name": "Istanbul Tech. Univ.", "country": "🇹🇷", "chance": "O'rta", "emoji": "🟡",
                 "note": "Yaxshi muhandislik"},
            ]
        else:
            recommendations = [
                {"name": "WIUT (Toshkent)", "country": "🇺🇿", "chance": "O'rta", "emoji": "🟡",
                 "note": "IELTS oshirish tavsiya"},
                {"name": "INHA University (Toshkent)", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "IELTS 5.0+ yetarli"},
                {"name": "METU (Turkiya)", "country": "🇹🇷", "chance": "Past", "emoji": "🔴",
                 "note": "Hali tayyorlanish kerak"},
            ]
    else:
        # O'zbekiston universitetlari (DTM asosida)
        if dtm_score and dtm_score >= 180:
            recommendations = [
                {"name": "O'zMU (NUU)", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": f"DTM {dtm_score} — grant imkoniyati bor"},
                {"name": "TDTU", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Texnika va muhandislik"},
                {"name": "SamDU", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Samarqand davlat universiteti"},
                {"name": "TUIT", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "IT va telekommunikatsiya"},
            ]
        elif score_pct >= 70:
            recommendations = [
                {"name": "TDTU", "country": "🇺🇿", "chance": "O'rta-Yuqori", "emoji": "🟡",
                 "note": "DTM balini oshirish tavsiya"},
                {"name": "SamDU", "country": "🇺🇿", "chance": "O'rta", "emoji": "🟡",
                 "note": "Samarqand — qulay"},
                {"name": "WIUT", "country": "🇺🇿", "chance": "O'rta", "emoji": "🟡",
                 "note": "Ingliz tilini ham o'rganing"},
            ]
        else:
            recommendations = [
                {"name": "Viloyat universitetlari", "country": "🇺🇿", "chance": "Yuqori", "emoji": "🟢",
                 "note": "Yaqin universitetlardan boshlang"},
                {"name": "DTM ballini oshiring", "country": "🎯", "chance": "—", "emoji": "📚",
                 "note": "Intensiv tayyorgarlik tavsiya"},
            ]

    return recommendations
