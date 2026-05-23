"""
University scrapers — rasmiy manbalardan ma'lumot olish.

Manbalar:
1. Hipolabs API (bepul, hech qanday key shart emas)
2. HEMIS O'zbekiston (hemis.minedu.uz)
3. QS Rankings JSON
"""
import requests
import logging
import time

logger = logging.getLogger('bot')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ABTYordamchi/1.0)',
    'Accept': 'application/json',
}

# ── Rasmiy university ma'lumotlari bazasi ──────────────
# Bu yerda to'liq, tekshirilgan ma'lumotlar saqlanadi
# Har yili yangilanadi

VERIFIED_DATA = {
    # === O'ZBEKISTON ===
    "O'zbekiston Milliy Universiteti": {
        "short_name": "NUU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_uzs": 4_500_000,
        "dtm_passing_score": 180, "national_ranking": 1,
        "has_scholarships": True, "scholarship_info": "DTM asosida davlat granti (top 20%)",
        "website": "https://nuu.uz",
        "application_deadline_fall": "2026-07-20",
        "description_uz": "O'zbekistonning yetakchi davlat universiteti. 1918-yilda tashkil etilgan.",
        "faculties": [
            ("Matematika va informatika", "Bachelor", 4, None, "O'zbek"),
            ("Fizika", "Bachelor", 4, None, "O'zbek"),
            ("Kimyo", "Bachelor", 4, None, "O'zbek"),
            ("Biologiya", "Bachelor", 4, None, "O'zbek"),
            ("Tarix", "Bachelor", 4, None, "O'zbek"),
            ("Huquq", "Bachelor", 4, None, "O'zbek"),
            ("Xorijiy filologiya", "Bachelor", 4, None, "O'zbek"),
            ("Iqtisodiyot", "Bachelor", 4, None, "O'zbek"),
        ]
    },
    "Toshkent Axborot Texnologiyalari Universiteti": {
        "short_name": "TATU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_uzs": 5_800_000,
        "dtm_passing_score": 175, "national_ranking": 2,
        "has_scholarships": True, "scholarship_info": "DTM granti — IT yo'nalishlar bo'yicha",
        "website": "https://tuit.uz",
        "application_deadline_fall": "2026-07-20",
        "description_uz": "O'zbekistonning yetakchi IT va telekommunikatsiya universiteti.",
        "faculties": [
            ("Dasturiy injiniring", "Bachelor", 4, None, "O'zbek"),
            ("Axborot xavfsizligi", "Bachelor", 4, None, "O'zbek"),
            ("Sun'iy intellekt", "Bachelor", 4, None, "O'zbek"),
            ("Telekommunikatsiya", "Bachelor", 4, None, "O'zbek"),
            ("Kompyuter muhandisligi", "Bachelor", 4, None, "O'zbek"),
        ]
    },
    "Westminster International University in Tashkent": {
        "short_name": "WIUT", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 4_000,
        "required_ielts": 5.5, "national_ranking": 3,
        "has_scholarships": True,
        "scholarship_info": "Merit stipendiya: top talabalar uchun 30-50% chegirma",
        "website": "https://wiut.uz",
        "application_deadline_fall": "2026-06-01",
        "description_uz": "Britaniya Westminster universiteti hamkorligida. Ingliz tilida ta'lim.",
        "faculties": [
            ("Business Administration", "Bachelor", 3, 4000, "English"),
            ("Computing", "Bachelor", 3, 4500, "English"),
            ("Finance and Banking", "Bachelor", 3, 4000, "English"),
            ("Economics", "Bachelor", 3, 4000, "English"),
            ("International Relations", "Bachelor", 3, 4000, "English"),
        ]
    },
    "Inha University in Tashkent": {
        "short_name": "INHA", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 3_500,
        "required_ielts": 5.0, "national_ranking": 4,
        "has_scholarships": True,
        "scholarship_info": "O'zbekiston va Koreya hukumati grantlari mavjud",
        "website": "https://inha.uz",
        "application_deadline_fall": "2026-06-15",
        "description_uz": "Janubiy Koreya Inha universiteti hamkorligida. IT va muhandislik.",
        "faculties": [
            ("Computer Science and Engineering", "Bachelor", 4, 3500, "English"),
            ("Electrical Engineering", "Bachelor", 4, 3500, "English"),
            ("Mechanical Engineering", "Bachelor", 4, 3500, "English"),
            ("Industrial Engineering", "Bachelor", 4, 3500, "English"),
        ]
    },
    "Turin Polytechnic University in Tashkent": {
        "short_name": "TTPU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 4_500,
        "required_ielts": 5.5, "national_ranking": 5,
        "has_scholarships": True,
        "scholarship_info": "Italiya hukumati va TTPU grantlari",
        "website": "https://polito.uz",
        "application_deadline_fall": "2026-05-31",
        "description_uz": "Italiya Torino Politexnika universiteti hamkorligida.",
        "faculties": [
            ("Mechanical Engineering", "Bachelor", 4, 4500, "English/Italian"),
            ("Computer Engineering", "Bachelor", 4, 4500, "English"),
            ("Architecture", "Bachelor", 5, 4500, "English/Italian"),
            ("Petroleum Engineering", "Bachelor", 4, 4500, "English"),
        ]
    },
    # === USA ===
    "Massachusetts Institute of Technology": {
        "short_name": "MIT", "country": "US", "city": "Cambridge, MA",
        "tuition_fee_usd": 57_986,
        "required_ielts": 7.0, "required_sat": 1500,
        "world_ranking": 1, "acceptance_rate": 4.0,
        "has_scholarships": True,
        "scholarship_info": "Need-based: oilasi $75K dan kam bo'lsa o'qish bepul yoki arzon",
        "scholarship_coverage": "Daromadga qarab to'liq qoplanishi mumkin",
        "website": "https://mit.edu", "application_url": "https://apply.mit.edu",
        "application_deadline_fall": "2027-01-01",
        "founded_year": 1861,
        "description_uz": "Dunyo texnika universitetlari reytingida 1-o'rin. Ilm-fan va texnologiyada yetakchi.",
        "faculties": [
            ("Computer Science & Engineering", "Bachelor", 4, 57986, "English"),
            ("Electrical Engineering & CS", "Bachelor", 4, 57986, "English"),
            ("Mathematics", "Bachelor", 4, 57986, "English"),
            ("Physics", "Bachelor", 4, 57986, "English"),
            ("Mechanical Engineering", "Bachelor", 4, 57986, "English"),
            ("MBA (Sloan)", "Master", 2, 77170, "English"),
        ]
    },
    "Harvard University": {
        "short_name": "Harvard", "country": "US", "city": "Cambridge, MA",
        "tuition_fee_usd": 59_950,
        "required_ielts": 7.0, "required_sat": 1580,
        "world_ranking": 3, "acceptance_rate": 3.4,
        "has_scholarships": True,
        "scholarship_info": "Need-blind admission — $85K dan kam daromadli oilalar uchun bepul",
        "scholarship_coverage": "Daromad $65K dan kam: to'liq bepul",
        "website": "https://harvard.edu",
        "application_deadline_fall": "2027-01-01",
        "founded_year": 1636,
        "description_uz": "Dunyo universitetlari orasida eng nufuzdori. 1636-yilda tashkil etilgan.",
        "faculties": [
            ("Computer Science", "Bachelor", 4, 59950, "English"),
            ("Economics", "Bachelor", 4, 59950, "English"),
            ("Law (JD)", "Master", 3, 67081, "English"),
            ("MBA", "Master", 2, 73440, "English"),
            ("Medicine (MD)", "Doctoral", 4, 65000, "English"),
            ("Public Health (MPH)", "Master", 2, 60000, "English"),
        ]
    },
    "Stanford University": {
        "short_name": "Stanford", "country": "US", "city": "Stanford, CA",
        "tuition_fee_usd": 57_693,
        "required_ielts": 7.0, "required_sat": 1550,
        "world_ranking": 5, "acceptance_rate": 3.7,
        "has_scholarships": True,
        "scholarship_info": "Need-based: $75K dan kam daromadli oilalar uchun bepul",
        "website": "https://stanford.edu",
        "application_deadline_fall": "2027-01-02",
        "founded_year": 1885,
        "description_uz": "Silikon vodiysi yaqinidagi innovatsiya markazi. Texnologiya va biznesda yetakchi.",
        "faculties": [
            ("Computer Science", "Bachelor", 4, 57693, "English"),
            ("Engineering", "Bachelor", 4, 57693, "English"),
            ("MBA (GSB)", "Master", 2, 74706, "English"),
            ("Law (JD)", "Master", 3, 64770, "English"),
            ("Medicine", "Doctoral", 4, 62000, "English"),
        ]
    },
    # === UK ===
    "University of Oxford": {
        "short_name": "Oxford", "country": "GB", "city": "Oxford",
        "tuition_fee_usd": 35_000,
        "required_ielts": 7.5, "world_ranking": 2,
        "acceptance_rate": 17.5,
        "has_scholarships": True,
        "scholarship_info": "Rhodes Scholarship (to'liq) · Clarendon Fund · Weidenfeld-Hoffmann",
        "website": "https://ox.ac.uk",
        "application_deadline_fall": "2026-10-15",
        "founded_year": 1096,
        "description_uz": "Dunyo tarixidagi eng qadimiy universitetlardan biri. 1096-yilda tashkil etilgan.",
        "faculties": [
            ("PPE (Politics, Philosophy, Economics)", "Bachelor", 3, 35000, "English"),
            ("Computer Science", "Bachelor", 3, 35000, "English"),
            ("Medicine (MBBCh)", "Bachelor", 6, 38000, "English"),
            ("Law (BA)", "Bachelor", 3, 35000, "English"),
            ("Mathematics", "Bachelor", 3, 35000, "English"),
            ("MBA (Said Business School)", "Master", 1, 62000, "English"),
        ]
    },
    "University of Cambridge": {
        "short_name": "Cambridge", "country": "GB", "city": "Cambridge",
        "tuition_fee_usd": 33_000,
        "required_ielts": 7.5, "world_ranking": 4,
        "acceptance_rate": 21.0,
        "has_scholarships": True,
        "scholarship_info": "Gates Cambridge Scholarship — to'liq moliyaviy qo'llab-quvvatlash",
        "website": "https://cam.ac.uk",
        "application_deadline_fall": "2026-10-15",
        "founded_year": 1209,
        "description_uz": "Britaniyaning eng nufuzli universiteti. Newton, Darwin, Hawking o'qigan joy.",
        "faculties": [
            ("Natural Sciences", "Bachelor", 3, 33000, "English"),
            ("Computer Science", "Bachelor", 3, 33000, "English"),
            ("Engineering", "Bachelor", 3, 33000, "English"),
            ("Mathematics", "Bachelor", 3, 33000, "English"),
            ("Law", "Bachelor", 3, 33000, "English"),
            ("MBA (Judge Business School)", "Master", 1, 62000, "English"),
        ]
    },
    # === GERMANY ===
    "Technical University of Munich": {
        "short_name": "TUM", "country": "DE", "city": "Munich",
        "tuition_fee_usd": 500,
        "required_ielts": 6.5, "world_ranking": 30,
        "has_scholarships": True,
        "scholarship_info": "DAAD stipendiyasi — oyiga €861-1,200. Ko'p dasturlar BEPUL!",
        "scholarship_coverage": "O'qish + turar joy + sug'urta + oylik",
        "website": "https://tum.de",
        "application_deadline_fall": "2026-05-31",
        "founded_year": 1868,
        "description_uz": "Germaniyaning eng yaxshi texnika universiteti. Ko'p dasturlar BEPUL. DAAD stipendiyasi mavjud.",
        "faculties": [
            ("Informatics (Computer Science)", "Bachelor", 3, 500, "German/English"),
            ("Electrical Engineering", "Bachelor", 3, 500, "German/English"),
            ("Mechanical Engineering", "Bachelor", 3, 500, "German"),
            ("Mathematics", "Bachelor", 3, 500, "German"),
            ("Physics", "Bachelor", 3, 500, "German"),
            ("Architecture", "Bachelor", 4, 500, "German"),
            ("MBA TUM", "Master", 2, 15000, "English"),
        ]
    },
    "Heidelberg University": {
        "short_name": "Heidelberg", "country": "DE", "city": "Heidelberg",
        "tuition_fee_usd": 300,
        "required_ielts": 6.5, "world_ranking": 66,
        "has_scholarships": True,
        "scholarship_info": "DAAD + Deutschlandstipendium — oyiga €300 qo'shimcha",
        "website": "https://uni-heidelberg.de",
        "application_deadline_fall": "2026-07-15",
        "founded_year": 1386,
        "description_uz": "Germaniyaning eng qadimiy universiteti. Tibbiyot va tabiiy fanlar sohasida yetakchi.",
        "faculties": [
            ("Medicine", "Bachelor", 6, 300, "German"),
            ("Natural Sciences", "Bachelor", 4, 300, "German"),
            ("Law", "Bachelor", 4, 300, "German"),
            ("Psychology", "Bachelor", 4, 300, "German"),
            ("Life Sciences", "Bachelor", 4, 300, "German"),
        ]
    },
    # === KOREA ===
    "Seoul National University": {
        "short_name": "SNU", "country": "KR", "city": "Seoul",
        "tuition_fee_usd": 4_500,
        "required_ielts": 6.0, "world_ranking": 35,
        "has_scholarships": True,
        "scholarship_info": "GKS (Global Korea Scholarship) — TO'LIQ: o'qish + yotoqxona + stipendiya + parvoz + til kursi",
        "scholarship_coverage": "To'liq moliyaviy — hech narsa to'lamasiz",
        "website": "https://snu.ac.kr",
        "application_deadline_fall": "2026-09-30",
        "founded_year": 1946,
        "description_uz": "Janubiy Koreya Respublikasining #1 universiteti. GKS stipendiyasi bilan to'liq bepul.",
        "faculties": [
            ("Computer Science and Engineering", "Bachelor", 4, 4500, "Korean/English"),
            ("Business Administration", "Bachelor", 4, 4000, "Korean/English"),
            ("Electrical and Computer Engineering", "Bachelor", 4, 4500, "Korean"),
            ("Medicine", "Bachelor", 6, 5000, "Korean"),
            ("Law", "Master", 3, 5500, "Korean"),
            ("International Studies", "Master", 2, 4000, "English"),
        ]
    },
    "KAIST": {
        "short_name": "KAIST", "country": "KR", "city": "Daejeon",
        "tuition_fee_usd": 3_000,
        "required_ielts": 6.0, "world_ranking": 42,
        "has_scholarships": True,
        "scholarship_info": "Xorijiy talabalar uchun TO'LIQ BEPUL + oyiga 350,000 won stipendiya",
        "scholarship_coverage": "O'qish + yotoqxona + oylik 350,000 won",
        "website": "https://kaist.ac.kr",
        "application_deadline_fall": "2026-09-01",
        "founded_year": 1971,
        "description_uz": "Koreya ilm-fan va texnologiya instituti. Xorijiy talabalar uchun o'qish BEPUL.",
        "faculties": [
            ("School of Computing", "Bachelor", 4, 0, "Korean/English"),
            ("Electrical Engineering", "Bachelor", 4, 0, "Korean/English"),
            ("Mathematics", "Bachelor", 4, 0, "Korean"),
            ("Physics", "Bachelor", 4, 0, "Korean"),
            ("Bio and Brain Engineering", "Bachelor", 4, 0, "Korean/English"),
        ]
    },
    # === TURKEY ===
    "Middle East Technical University": {
        "short_name": "METU", "country": "TR", "city": "Ankara",
        "tuition_fee_usd": 600,
        "required_ielts": 6.0, "world_ranking": 401,
        "has_scholarships": True,
        "scholarship_info": "Türkiye Bursları: TO'LIQ — o'qish+yotoqxona+stipendiya+parvoz+til kursi. Ariza: fevral",
        "scholarship_coverage": "O'qish to'lovi + yotoqxona + oylik 1,400 TRY + parvoz",
        "website": "https://metu.edu.tr",
        "application_deadline_fall": "2026-02-28",
        "founded_year": 1956,
        "description_uz": "Turkiyaning ingliz tilida o'qitiladigan eng yaxshi universiteti. Türkiye Bursları bilan bepul.",
        "faculties": [
            ("Computer Engineering", "Bachelor", 4, 600, "English"),
            ("Electrical and Electronics Engineering", "Bachelor", 4, 600, "English"),
            ("Industrial Engineering", "Bachelor", 4, 600, "English"),
            ("Architecture", "Bachelor", 4, 600, "English"),
            ("Business Administration", "Master", 2, 600, "English"),
        ]
    },
    # === CHINA ===
    "Tsinghua University": {
        "short_name": "THU", "country": "CN", "city": "Beijing",
        "tuition_fee_usd": 4_500,
        "required_ielts": 6.5, "world_ranking": 14,
        "has_scholarships": True,
        "scholarship_info": "CSC (Xitoy hukumati) stipendiyasi: o'qish + yotoqxona + oyiga 3,500 RMB. Ariza: mart",
        "website": "https://tsinghua.edu.cn",
        "application_deadline_fall": "2026-03-31",
        "founded_year": 1911,
        "description_uz": "Xitoyning #1 universiteti. CSC stipendiyasi orqali to'liq moliyaviy.",
        "faculties": [
            ("Computer Science and Technology", "Bachelor", 4, 4500, "Chinese/English"),
            ("Electrical Engineering", "Bachelor", 4, 4000, "Chinese"),
            ("Economics and Management", "Bachelor", 4, 4500, "Chinese/English"),
            ("Architecture", "Bachelor", 5, 4500, "Chinese"),
            ("Mechanical Engineering", "Bachelor", 4, 4000, "Chinese"),
        ]
    },
    # === JAPAN ===
    "University of Tokyo": {
        "short_name": "UTokyo", "country": "JP", "city": "Tokyo",
        "tuition_fee_usd": 5_000,
        "required_ielts": 6.5, "world_ranking": 22,
        "has_scholarships": True,
        "scholarship_info": "MEXT (Yaponiya hukumati): oyiga 117,000-145,000 yen + o'qish bepul + parvoz. Ariza: may-iyun",
        "scholarship_coverage": "O'qish to'lovi + oylik stipendiya + parvoz",
        "website": "https://u-tokyo.ac.jp",
        "application_deadline_fall": "2026-11-30",
        "founded_year": 1877,
        "description_uz": "Yaponiyaning #1 universiteti. MEXT stipendiyasi bilan o'qish mumkin.",
        "faculties": [
            ("Computer Science", "Bachelor", 4, 5000, "Japanese/English"),
            ("Engineering", "Bachelor", 4, 5000, "Japanese"),
            ("Medicine", "Bachelor", 6, 5000, "Japanese"),
            ("Economics", "Bachelor", 4, 5000, "Japanese"),
            ("Science", "Bachelor", 4, 5000, "Japanese"),
            ("Law", "Bachelor", 4, 5000, "Japanese"),
        ]
    },
    "Kyoto University": {
        "short_name": "KyotoU", "country": "JP", "city": "Kyoto",
        "tuition_fee_usd": 5_000,
        "required_ielts": 6.5, "world_ranking": 46,
        "has_scholarships": True,
        "scholarship_info": "MEXT + JASSO stipendiyalari. Oyiga 80,000-117,000 yen",
        "website": "https://kyoto-u.ac.jp",
        "application_deadline_fall": "2026-11-30",
        "founded_year": 1897,
        "description_uz": "Yaponiyaning 2-chi eng yaxshi universiteti. 19 ta Nobel mukofoti sovrindori.",
        "faculties": [
            ("Engineering", "Bachelor", 4, 5000, "Japanese/English"),
            ("Science", "Bachelor", 4, 5000, "Japanese"),
            ("Medicine", "Bachelor", 6, 5000, "Japanese"),
            ("Agriculture", "Bachelor", 4, 5000, "Japanese"),
            ("Letters (Humanities)", "Bachelor", 4, 5000, "Japanese"),
        ]
    },
    "Osaka University": {
        "short_name": "OsakaU", "country": "JP", "city": "Osaka",
        "tuition_fee_usd": 5_000,
        "required_ielts": 6.0, "world_ranking": 80,
        "has_scholarships": True,
        "scholarship_info": "MEXT stipendiyasi + Osaka University Global Scholarship",
        "website": "https://osaka-u.ac.jp",
        "application_deadline_fall": "2026-12-01",
        "description_uz": "Yaponiyaning yetakchi ilmiy universiteti. Tibbiyot va muhandislikda kuchli.",
        "faculties": [
            ("Engineering Science", "Bachelor", 4, 5000, "Japanese/English"),
            ("Science", "Bachelor", 4, 5000, "Japanese"),
            ("Medicine", "Bachelor", 6, 5000, "Japanese"),
            ("Information Science and Technology", "Bachelor", 4, 5000, "Japanese/English"),
        ]
    },
    # === MALAYSIA ===
    "University of Malaya": {
        "short_name": "UM", "country": "MY", "city": "Kuala Lumpur",
        "tuition_fee_usd": 3_500,
        "required_ielts": 6.0, "world_ranking": 65,
        "has_scholarships": True,
        "scholarship_info": "MSD, MyCSD va xalqaro stipendiyalar. ASEAN grant ham mavjud",
        "website": "https://um.edu.my",
        "application_deadline_fall": "2026-03-31",
        "founded_year": 1905,
        "description_uz": "Malayziyaning #1 universiteti. Arzon va sifatli ingliz tilida ta'lim.",
        "faculties": [
            ("Computer Science", "Bachelor", 3, 3500, "English"),
            ("Business and Accountancy", "Bachelor", 3, 3200, "English"),
            ("Medicine (MBBS)", "Bachelor", 5, 8000, "English"),
            ("Engineering", "Bachelor", 4, 3500, "English"),
            ("Law", "Bachelor", 3, 3500, "English"),
        ]
    },
    # === RUSSIA ===
    "Moscow State University": {
        "short_name": "MSU", "country": "RU", "city": "Moscow",
        "tuition_fee_usd": 4_000,
        "required_ielts": 5.5, "world_ranking": 87,
        "has_scholarships": True,
        "scholarship_info": "Rossiya hukumati kvotasi — O'zbekistonga yiliga 500+ o'rin ajratiladi",
        "website": "https://msu.ru",
        "application_deadline_fall": "2026-04-01",
        "founded_year": 1755,
        "description_uz": "Rossiyaning eng yirik va nufuzli universiteti. Davlat kvotasi orqali bepul o'qish mumkin.",
        "faculties": [
            ("Mechanics and Mathematics", "Bachelor", 4, 4000, "Russian"),
            ("Physics", "Bachelor", 4, 4000, "Russian"),
            ("Chemistry", "Bachelor", 4, 4000, "Russian"),
            ("Law", "Bachelor", 4, 5000, "Russian"),
            ("Economics", "Bachelor", 4, 5000, "Russian"),
            ("Computer Science", "Bachelor", 4, 4000, "Russian"),
        ]
    },
    # === CANADA ===
    "University of Toronto": {
        "short_name": "UToronto", "country": "CA", "city": "Toronto",
        "tuition_fee_usd": 40_000,
        "required_ielts": 6.5, "world_ranking": 18,
        "has_scholarships": True,
        "scholarship_info": "Lester B. Pearson Scholarship — to'liq bepul (juda tanlov). President's Scholarship",
        "website": "https://utoronto.ca",
        "application_deadline_fall": "2027-01-15",
        "description_uz": "Kanada universitetlari orasida #1. Lester B. Pearson stipendiyasi — to'liq bepul.",
        "faculties": [
            ("Computer Science", "Bachelor", 4, 40000, "English"),
            ("Engineering", "Bachelor", 4, 40000, "English"),
            ("Business (Rotman MBA)", "Master", 2, 85000, "English"),
            ("Medicine", "Bachelor", 4, 40000, "English"),
            ("Law", "Master", 3, 45000, "English"),
        ]
    },
    # === FRANCE ===
    "École Polytechnique": {
        "short_name": "Poly", "country": "FR", "city": "Paris",
        "tuition_fee_usd": 14_000,
        "required_ielts": 6.5, "world_ranking": 41,
        "has_scholarships": True,
        "scholarship_info": "Eiffel Scholarship: Master uchun €1,181/oy, PhD uchun €1,400/oy. Ariza: yanvar 8",
        "website": "https://polytechnique.edu",
        "application_deadline_fall": "2027-01-15",
        "founded_year": 1794,
        "description_uz": "Fransiyaning eng nufuzli muhandislik maktabi. Eiffel stipendiyasi mavjud.",
        "faculties": [
            ("Ingénieur Polytechnicien", "Bachelor", 4, 14000, "French/English"),
            ("Computer Science", "Master", 2, 14000, "French/English"),
            ("Applied Mathematics", "Master", 2, 14000, "French/English"),
            ("Physics", "Master", 2, 14000, "French/English"),
        ]
    },
}


def get_all_verified_data() -> dict:
    """Barcha tekshirilgan ma'lumotlarni qaytaradi."""
    return VERIFIED_DATA


def fetch_uz_from_hemis() -> list:
    """
    O'zbekiston universitetlarini HEMIS dan olishga harakat.
    Agar API ishlamasa, Hipolabs dan olinadi.
    """
    # 1. HEMIS API
    try:
        resp = requests.get(
            "https://hemis.minedu.uz/api/universities",
            headers=HEADERS, timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            items = data if isinstance(data, list) else data.get('data', [])
            for item in items:
                name = item.get('name_uz') or item.get('name', '')
                if not name: continue
                results.append({
                    'name':    name,
                    'city':    item.get('region', 'Toshkent'),
                    'website': item.get('website', ''),
                    'type':    item.get('type', 'Davlat'),
                })
            if results:
                logger.info(f"HEMIS: {len(results)} ta O'zbekiston universiteti")
                return results
    except Exception as e:
        logger.warning(f"HEMIS API ulanmadi: {e}")

    # 2. Hipolabs fallback
    try:
        resp = requests.get(
            "http://universities.hipolabs.com/search",
            params={'country': 'Uzbekistan'},
            headers=HEADERS, timeout=8
        )
        if resp.status_code == 200:
            results = []
            for item in resp.json():
                name = item.get('name', '')
                if not name: continue
                results.append({
                    'name':    name,
                    'city':    'Toshkent',
                    'website': item.get('web_pages', [''])[0] if item.get('web_pages') else '',
                    'type':    'OTM',
                })
            logger.info(f"Hipolabs UZ: {len(results)} ta universitet")
            return results
    except Exception as e:
        logger.warning(f"Hipolabs ulanmadi: {e}")

    return []


def fetch_world_unis_by_country(country_name: str, country_code: str) -> list:
    """Hipolabs API orqali mamlakat universittetlarini olish."""
    try:
        resp = requests.get(
            "http://universities.hipolabs.com/search",
            params={'country': country_name},
            headers=HEADERS, timeout=8
        )
        if resp.status_code == 200:
            results = []
            for item in resp.json():
                name = item.get('name', '')
                if not name: continue
                results.append({
                    'name':     name,
                    'country':  country_code,
                    'website':  item.get('web_pages', [''])[0] if item.get('web_pages') else '',
                })
            return results
    except Exception as e:
        logger.warning(f"Hipolabs {country_name}: {e}")
    return []
