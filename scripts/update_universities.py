"""
Universitetlar rasmiy ma'lumotlari - 2026 yil
Barcha muddatlar va narxlar rasmiy saytlardan
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('USE_SQLITE', 'true')
django.setup()

from apps.universities.models import University, Faculty
from datetime import date

print("🏫 Universitetlar yangilanmoqda (2026 rasmiy ma'lumotlar)...")

# ══════════════════════════════════════════════════════
# RASMIY MA'LUMOTLAR (har yili yangilanadi)
# Manba: QS Rankings 2025, rasmiy saytlar
# Oxirgi yangilanish: 2026
# ══════════════════════════════════════════════════════

UNIVERSITIES = [

    # ── O'ZBEKISTON ──────────────────────────────────
    {
        "name": "O'zbekiston Milliy Universiteti",
        "short_name": "NUU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_uzs": 5200000,  # 2026 narx
        "has_scholarships": True,
        "scholarship_info": "DTM 189+ ball davlat granti, 170-188 imtiyozli",
        "dtm_passing_score": 170,
        "national_ranking": 1,
        "is_active": True, "is_featured": True,
        "founded_year": 1918,
        "website": "https://nuu.uz",
        "application_url": "https://nuu.uz/abiturient",
        "application_deadline_fall": date(2026, 7, 15),  # DTM natijalari keyin
        "description_uz": "O'zbekistonning yetakchi davlat universiteti. 1918-yilda tashkil etilgan. 20+ fakultet, 15,000+ talaba.",
        "acceptance_rate": "40.0",
    },
    {
        "name": "Toshkent Axborot Texnologiyalari Universiteti",
        "short_name": "TATU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_uzs": 7800000,
        "has_scholarships": True,
        "scholarship_info": "DTM 185+ ball davlat granti",
        "dtm_passing_score": 185,
        "national_ranking": 2,
        "is_active": True, "is_featured": True,
        "founded_year": 1955,
        "website": "https://tuit.uz",
        "application_deadline_fall": date(2026, 7, 15),
        "description_uz": "IT va dasturlash sohasi bo'yicha O'zbekistondagi eng yaxshi davlat universiteti.",
    },
    {
        "name": "Westminster International University in Tashkent",
        "short_name": "WIUT", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 5200,   # 2026 narx (rasmiy sayt)
        "has_scholarships": True,
        "scholarship_info": "50% gacha merit scholarship, Early Bird 10% chegirma",
        "required_ielts": 5.5,
        "national_ranking": 3,
        "is_active": True, "is_featured": True,
        "founded_year": 2002,
        "website": "https://wiut.uz",
        "application_url": "https://wiut.uz/admissions",
        "application_deadline_fall": date(2026, 6, 30),
        "description_uz": "Britaniya University of Westminster bilan hamkorlik. Diplom UK da tan olinadi.",
    },
    {
        "name": "Inha University in Tashkent",
        "short_name": "IUT", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 4800,
        "has_scholarships": True,
        "scholarship_info": "Korea-Uzbekistan scholarship, Merit based 30-50%",
        "required_ielts": 5.0,
        "national_ranking": 4,
        "is_active": True, "is_featured": True,
        "founded_year": 2014,
        "website": "https://inha.uz",
        "application_url": "https://inha.uz/admissions",
        "application_deadline_fall": date(2026, 6, 15),
        "description_uz": "Janubiy Koreya INHA University hamkorligida. IT, muhandislik yo'nalishlari.",
    },
    {
        "name": "Turin Polytechnic University in Tashkent",
        "short_name": "TTPU", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 5500,
        "has_scholarships": True,
        "scholarship_info": "Italian Government scholarship, Merit 20-40%",
        "required_ielts": 5.5,
        "national_ranking": 5,
        "is_active": True, "is_featured": True,
        "founded_year": 2009,
        "website": "https://polito.uz",
        "application_url": "https://polito.uz/en/admissions",
        "application_deadline_fall": date(2026, 6, 1),
        "description_uz": "Italiya Politecnico di Torino hamkorligida. Muhandislik va texnologiya.",
    },
    {
        "name": "Management Development Institute of Singapore in Tashkent",
        "short_name": "MDIST", "country": "UZ", "city": "Toshkent",
        "tuition_fee_usd": 4500,
        "has_scholarships": True,
        "required_ielts": 5.5,
        "national_ranking": 6,
        "is_active": True,
        "founded_year": 2002,
        "website": "https://mdist.uz",
        "application_deadline_fall": date(2026, 6, 30),
        "description_uz": "Singapur MDIS bilan hamkorlik. Biznes va IT yo'nalishlari.",
    },
    {
        "name": "Samarqand Davlat Universiteti",
        "short_name": "SamDU", "country": "UZ", "city": "Samarqand",
        "tuition_fee_uzs": 4800000,
        "has_scholarships": True,
        "dtm_passing_score": 160,
        "national_ranking": 7,
        "is_active": True,
        "founded_year": 1927,
        "website": "https://samdu.uz",
        "application_deadline_fall": date(2026, 7, 15),
        "description_uz": "O'rta Osiyoning qadimiy va nufuzli universitetlaridan biri.",
    },
    {
        "name": "Toshkent Tibbiyot Akademiyasi",
        "short_name": "TMA", "country": "UZ", "city": "Toshkent",
        "tuition_fee_uzs": 12000000,
        "has_scholarships": True,
        "dtm_passing_score": 180,
        "national_ranking": 8,
        "is_active": True,
        "founded_year": 1919,
        "website": "https://tma.uz",
        "application_deadline_fall": date(2026, 7, 15),
        "description_uz": "O'zbekistondagi eng yaxshi tibbiyot universiteti.",
    },

    # ── QO'SHMA SHTATLAR ──────────────────────────────
    {
        "name": "Massachusetts Institute of Technology",
        "short_name": "MIT", "country": "US", "city": "Cambridge, MA",
        "tuition_fee_usd": 59750,   # 2025-26 academic year (rasmiy)
        "has_scholarships": True,
        "scholarship_info": "Need-blind admission. Oila daromadi $100k dan kam bo'lsa o'rtacha $0 to'lov. Jami $50k+ grant mumkin.",
        "required_ielts": 7.0,
        "required_sat": 1510,
        "world_ranking": 1,
        "qs_ranking": 1,
        "is_active": True, "is_featured": True,
        "founded_year": 1861,
        "website": "https://mit.edu",
        "application_url": "https://apply.mit.edu",
        "application_deadline_fall": date(2026, 1, 1),   # Early Action: Nov 1, Regular: Jan 1
        "description_uz": "Dunyo #1 texnika universiteti. 97 ta Nobel laureati. Need-blind moliyaviy yordam.",
        "acceptance_rate": "3.9",
        "total_students": 11500,
        "international_students": 3800,
    },
    {
        "name": "Harvard University",
        "short_name": "Harvard", "country": "US", "city": "Cambridge, MA",
        "tuition_fee_usd": 59076,   # 2025-26 (harvard.edu)
        "has_scholarships": True,
        "scholarship_info": "Need-blind for US, need-aware for international. Oila daromadi $85k dan kam = to'liq bepul. O'rtacha grant $53,000.",
        "required_ielts": 7.0,
        "required_sat": 1580,
        "world_ranking": 4,
        "qs_ranking": 4,
        "is_active": True, "is_featured": True,
        "founded_year": 1636,
        "website": "https://harvard.edu",
        "application_url": "https://college.harvard.edu/admissions",
        "application_deadline_fall": date(2026, 1, 1),   # Regular: Jan 1
        "description_uz": "1636-yilda tashkil etilgan. Dunyo eng nufuzli universiteti. 161 Nobel laureati.",
        "acceptance_rate": "3.6",
        "total_students": 21000,
    },
    {
        "name": "Stanford University",
        "short_name": "Stanford", "country": "US", "city": "Stanford, CA",
        "tuition_fee_usd": 62484,   # 2025-26 (stanford.edu)
        "has_scholarships": True,
        "scholarship_info": "Oila daromadi $75k dan kam = to'liq bepul. $150k dan kam = 10% dan kam to'lov.",
        "required_ielts": 7.0,
        "required_sat": 1550,
        "world_ranking": 5,
        "qs_ranking": 5,
        "is_active": True, "is_featured": True,
        "founded_year": 1885,
        "website": "https://stanford.edu",
        "application_url": "https://admission.stanford.edu",
        "application_deadline_fall": date(2026, 1, 2),
        "description_uz": "Silicon Valley qalbi. Texnologiya va tadbirkorlik markazi. Google, Netflix, Yahoo asoschilari.",
        "acceptance_rate": "3.7",
    },
    {
        "name": "University of California, Berkeley",
        "short_name": "UC Berkeley", "country": "US", "city": "Berkeley, CA",
        "tuition_fee_usd": 44066,   # xorijiy talabalar uchun 2025-26
        "has_scholarships": True,
        "scholarship_info": "International students uchun cheklangan grant. Merit va need-based stipendiyalar mavjud.",
        "required_ielts": 6.5,
        "required_sat": 1420,
        "world_ranking": 12,
        "qs_ranking": 12,
        "is_active": True, "is_featured": True,
        "founded_year": 1868,
        "website": "https://berkeley.edu",
        "application_url": "https://apply.universityofcalifornia.edu",
        "application_deadline_fall": date(2025, 11, 30),  # UC muddat: Nov 30
        "description_uz": "Davlat universitetlari ichida dunyo #1. 107 Nobel laureati. CS va Engineering kuchli.",
        "acceptance_rate": "11.6",
    },

    # ── BUYUK BRITANIYA ───────────────────────────────
    {
        "name": "University of Oxford",
        "short_name": "Oxford", "country": "GB", "city": "Oxford",
        "tuition_fee_usd": 37510,   # 2025-26 international (ox.ac.uk)
        "has_scholarships": True,
        "scholarship_info": "Rhodes Scholarship (to'liq + stipendiya). Clarendon Fund. Oxford-Weidenfeld. 100+ scholarship dasturi.",
        "required_ielts": 7.5,
        "world_ranking": 3,
        "qs_ranking": 3,
        "is_active": True, "is_featured": True,
        "founded_year": 1096,
        "website": "https://ox.ac.uk",
        "application_url": "https://www.ox.ac.uk/admissions/undergraduate/applying-to-oxford",
        "application_deadline_fall": date(2025, 10, 15),  # UCAS muddat: Oct 15!
        "description_uz": "Dunyo eng qadimiy universiteti (1096). 73 Nobel laureati. Oxford Interview jarayoni.",
        "acceptance_rate": "14.3",
    },
    {
        "name": "University of Cambridge",
        "short_name": "Cambridge", "country": "GB", "city": "Cambridge",
        "tuition_fee_usd": 36000,   # 2025-26 international
        "has_scholarships": True,
        "scholarship_info": "Gates Cambridge Scholarship (to'liq, 90 ta). Cambridge Trust. Commonwealth Scholarship.",
        "required_ielts": 7.5,
        "world_ranking": 2,
        "qs_ranking": 2,
        "is_active": True, "is_featured": True,
        "founded_year": 1209,
        "website": "https://cam.ac.uk",
        "application_url": "https://www.undergraduate.study.cam.ac.uk/applying",
        "application_deadline_fall": date(2025, 10, 15),  # UCAS: Oct 15
        "description_uz": "Nyuton, Darvin, Hawking universiteti. 121 Nobel laureati. Gates Cambridge Scholarship.",
        "acceptance_rate": "17.6",
    },
    {
        "name": "Imperial College London",
        "short_name": "Imperial", "country": "GB", "city": "London",
        "tuition_fee_usd": 43000,   # 2025-26
        "has_scholarships": True,
        "scholarship_info": "Imperial College Scholarships. President's PhD Scholarship. External scholarships.",
        "required_ielts": 6.5,
        "world_ranking": 8,
        "qs_ranking": 8,
        "is_active": True, "is_featured": True,
        "founded_year": 1907,
        "website": "https://imperial.ac.uk",
        "application_url": "https://www.imperial.ac.uk/study/apply/",
        "application_deadline_fall": date(2026, 1, 15),
        "description_uz": "STEM sohasi bo'yicha Yevropa #1. Texnologiya va tibbiyot yo'nalishlari.",
    },

    # ── GERMANIYA ─────────────────────────────────────
    {
        "name": "Technical University of Munich",
        "short_name": "TUM", "country": "DE", "city": "Munich",
        "tuition_fee_usd": 300,     # Semestr uchun admin fee (to'lov yo'q!)
        "has_scholarships": True,
        "scholarship_info": "DAAD: oyiga €934 (2026). Deutschlandstipendium €300/oy. To'liq bepul o'qish!",
        "required_ielts": 6.5,
        "world_ranking": 30,
        "qs_ranking": 30,
        "is_active": True, "is_featured": True,
        "founded_year": 1868,
        "website": "https://tum.de",
        "application_url": "https://www.tum.de/en/studies/application",
        "application_deadline_fall": date(2026, 5, 31),  # Winter semester
        "description_uz": "Germaniya #1 texnika universiteti. O'qish BEPUL! DAAD stipendiyasi.",
        "acceptance_rate": "8.0",
    },
    {
        "name": "Heidelberg University",
        "short_name": "Heidelberg", "country": "DE", "city": "Heidelberg",
        "tuition_fee_usd": 200,     # Semestr uchun minimal
        "has_scholarships": True,
        "scholarship_info": "DAAD stipendiyasi. Bepul o'qish (faqat semestr to'lovi).",
        "required_ielts": 6.5,
        "world_ranking": 65,
        "qs_ranking": 65,
        "is_active": True,
        "founded_year": 1386,
        "website": "https://uni-heidelberg.de",
        "application_url": "https://www.uni-heidelberg.de/en/study/international-students",
        "application_deadline_fall": date(2026, 5, 15),
        "description_uz": "Germaniyaning eng qadimiy universiteti (1386). Tibbiyot va tabiiy fanlar.",
    },

    # ── JANUBIY KOREYA ────────────────────────────────
    {
        "name": "Seoul National University",
        "short_name": "SNU", "country": "KR", "city": "Seoul",
        "tuition_fee_usd": 4900,    # 2025-26 (snu.ac.kr)
        "has_scholarships": True,
        "scholarship_info": "GKS (Korean Government Scholarship): to'liq (o'qish + $1000/oy + parvoz + sug'urta). SNU Excellence Award.",
        "required_ielts": 6.0,
        "world_ranking": 31,
        "qs_ranking": 31,
        "is_active": True, "is_featured": True,
        "founded_year": 1946,
        "website": "https://snu.ac.kr",
        "application_url": "https://oia.snu.ac.kr/",
        "application_deadline_fall": date(2026, 9, 15),  # Spring: Mar 15
        "description_uz": "Koreya #1 universiteti. GKS stipendiyasi bilan to'liq bepul o'qish mumkin.",
        "acceptance_rate": "15.0",
    },
    {
        "name": "Korea Advanced Institute of Science and Technology",
        "short_name": "KAIST", "country": "KR", "city": "Daejeon",
        "tuition_fee_usd": 0,       # KAIST ajoyib — to'liq stipendiya bilan bepul!
        "has_scholarships": True,
        "scholarship_info": "KAIST Undergraduate Scholarship: TO'LIQ (barcha xorijiy talabalar). Qo'shimcha oylik $350.",
        "required_ielts": 6.0,
        "world_ranking": 42,
        "qs_ranking": 42,
        "is_active": True, "is_featured": True,
        "founded_year": 1971,
        "website": "https://kaist.ac.kr",
        "application_url": "https://admission.kaist.ac.kr/intl-undergraduate/",
        "application_deadline_fall": date(2025, 11, 14),  # Fall 2026: Nov 2025
        "description_uz": "Barcha xorijiy talabalar uchun TO'LIQ BEPUL! +oyiga $350 stipendiya. Dunyodagi eng yaxshi IT universiteti.",
        "acceptance_rate": "7.0",
    },
    {
        "name": "Yonsei University",
        "short_name": "Yonsei", "country": "KR", "city": "Seoul",
        "tuition_fee_usd": 9200,
        "has_scholarships": True,
        "scholarship_info": "GKS. Yonsei Scholarship 50-100%. POSCO scholarship.",
        "required_ielts": 5.5,
        "world_ranking": 56,
        "qs_ranking": 56,
        "is_active": True, "is_featured": True,
        "founded_year": 1885,
        "website": "https://yonsei.ac.kr",
        "application_url": "https://oia.yonsei.ac.kr/index.asp",
        "application_deadline_fall": date(2026, 3, 15),
        "description_uz": "SKY universitetlaridan biri. Biznes va IT kuchli. Seuldagi eng nufuzli xususiy universitetlardan.",
    },

    # ── YAPONIYA ──────────────────────────────────────
    {
        "name": "University of Tokyo",
        "short_name": "UTokyo", "country": "JP", "city": "Tokyo",
        "tuition_fee_usd": 5170,    # 2025-26 (u-tokyo.ac.jp)
        "has_scholarships": True,
        "scholarship_info": "MEXT (Monbukagakusho): TO'LIQ (o'qish + ¥117,000/oy + parvoz). JASSO stipendiyasi. G30 dasturi ingliz tilida.",
        "required_ielts": 6.5,
        "world_ranking": 28,
        "qs_ranking": 28,
        "is_active": True, "is_featured": True,
        "founded_year": 1877,
        "website": "https://u-tokyo.ac.jp",
        "application_url": "https://www.u-tokyo.ac.jp/en/prospective-students/undergrad_application.html",
        "application_deadline_fall": date(2026, 11, 30),
        "description_uz": "Yaponiya #1. MEXT stipendiyasi bilan to'liq bepul. G30 ingliz tilida dasturlar.",
    },
    {
        "name": "Kyoto University",
        "short_name": "KyotoU", "country": "JP", "city": "Kyoto",
        "tuition_fee_usd": 5170,
        "has_scholarships": True,
        "scholarship_info": "MEXT stipendiyasi. Kyoto University Fellowship. JASSO.",
        "required_ielts": 6.0,
        "world_ranking": 46,
        "qs_ranking": 46,
        "is_active": True, "is_featured": True,
        "founded_year": 1897,
        "website": "https://kyoto-u.ac.jp",
        "application_url": "https://www.kyoto-u.ac.jp/en/education-campus/education",
        "application_deadline_fall": date(2026, 10, 31),
        "description_uz": "Yaponiya #2. 16 Nobel laureati. Kimyo va biologiya sohasida jahon lideri.",
    },

    # ── TURKIYA ───────────────────────────────────────
    {
        "name": "Middle East Technical University",
        "short_name": "METU", "country": "TR", "city": "Ankara",
        "tuition_fee_usd": 850,     # 2025-26 yillik (metu.edu.tr)
        "has_scholarships": True,
        "scholarship_info": "Türkiye Bursları (Turkiya hukumati): TO'LIQ (o'qish + uy + ₺900/oy + parvoz + sog'liqni saqlash). O'zbekistonliklar uchun ajratilgan kvota!",
        "required_ielts": 6.0,
        "world_ranking": 401,
        "qs_ranking": 401,
        "is_active": True, "is_featured": True,
        "founded_year": 1956,
        "website": "https://metu.edu.tr",
        "application_url": "https://oidb.metu.edu.tr/en/international-students",
        "application_deadline_fall": date(2026, 2, 28),  # Türkiye Bursları: Feb
        "description_uz": "Turkiyaning ingliz tilida eng yaxshi texnika universiteti. Türkiye Bursları bilan to'liq bepul!",
    },
    {
        "name": "Bogazici University",
        "short_name": "Bogazici", "country": "TR", "city": "Istanbul",
        "tuition_fee_usd": 600,
        "has_scholarships": True,
        "scholarship_info": "Türkiye Bursları to'liq stipendiya. YÖK scholarship.",
        "required_ielts": 6.0,
        "world_ranking": 451,
        "qs_ranking": 451,
        "is_active": True, "is_featured": True,
        "founded_year": 1863,
        "website": "https://bogazici.edu.tr",
        "application_url": "https://international.boun.edu.tr/",
        "application_deadline_fall": date(2026, 2, 28),
        "description_uz": "Istanbul qal'asi yonida. Turkiyaning eng prestijli xususiy universiteti. Ingliz tilida.",
    },

    # ── XITOY ─────────────────────────────────────────
    {
        "name": "Tsinghua University",
        "short_name": "Tsinghua", "country": "CN", "city": "Beijing",
        "tuition_fee_usd": 4400,    # 2025-26
        "has_scholarships": True,
        "scholarship_info": "CSC (Xitoy hukumati): to'liq (o'qish + ¥3500/oy + turar joy). Tsinghua University Scholarship. Belt and Road scholarship.",
        "required_ielts": 6.5,
        "world_ranking": 14,
        "qs_ranking": 14,
        "is_active": True, "is_featured": True,
        "founded_year": 1911,
        "website": "https://tsinghua.edu.cn",
        "application_url": "https://www.tsinghua.edu.cn/en/Admissions.htm",
        "application_deadline_fall": date(2026, 3, 31),
        "description_uz": "Xitoy #1. Injiniring va texnologiyada jahon top-15. CSC scholarship to'liq bepul.",
    },
    {
        "name": "Peking University",
        "short_name": "PKU", "country": "CN", "city": "Beijing",
        "tuition_fee_usd": 4200,
        "has_scholarships": True,
        "scholarship_info": "CSC Government scholarship. PKU scholarship. Yenching Academy.",
        "required_ielts": 6.5,
        "world_ranking": 17,
        "qs_ranking": 17,
        "is_active": True, "is_featured": True,
        "founded_year": 1898,
        "website": "https://pku.edu.cn",
        "application_url": "https://www.oir.pku.edu.cn/en/",
        "application_deadline_fall": date(2026, 3, 15),
        "description_uz": "Xitoy #2. Gumanitar va tabiiy fanlar kuchli. CSC scholarship.",
    },

    # ── MALAYZIYA ─────────────────────────────────────
    {
        "name": "University of Malaya",
        "short_name": "UM", "country": "MY", "city": "Kuala Lumpur",
        "tuition_fee_usd": 3800,    # 2025-26
        "has_scholarships": True,
        "scholarship_info": "Malaysian International Scholarship (MIS). UM Excellence Award. ASEAN scholarship.",
        "required_ielts": 6.0,
        "world_ranking": 65,
        "qs_ranking": 65,
        "is_active": True, "is_featured": True,
        "founded_year": 1949,
        "website": "https://um.edu.my",
        "application_url": "https://www.um.edu.my/study-at-um/international-students",
        "application_deadline_fall": date(2026, 4, 30),
        "description_uz": "Janubi-Sharqiy Osiyo #1. Yashash narxi arzon. O'zbek talabalar ko'p.",
    },

    # ── SINGAPUR ──────────────────────────────────────
    {
        "name": "National University of Singapore",
        "short_name": "NUS", "country": "SG", "city": "Singapore",
        "tuition_fee_usd": 18600,   # 2025-26 xorijiy talabalar
        "has_scholarships": True,
        "scholarship_info": "NUS scholarship. ASEAN scholarship. Research scholarship. Singapore Government bursary.",
        "required_ielts": 6.5,
        "world_ranking": 8,
        "qs_ranking": 8,
        "is_active": True, "is_featured": True,
        "founded_year": 1905,
        "website": "https://nus.edu.sg",
        "application_url": "https://www.nus.edu.sg/oam/apply-to-nus",
        "application_deadline_fall": date(2026, 3, 19),
        "description_uz": "Osiyo #1. Dunyo top-10. IT, muhandislik va biznes sohasida kuchli.",
        "acceptance_rate": "5.0",
    },

    # ── AVSTRALIYA ────────────────────────────────────
    {
        "name": "University of Melbourne",
        "short_name": "UniMelb", "country": "AU", "city": "Melbourne",
        "tuition_fee_usd": 38000,   # 2026 yillik (unimelb.edu.au)
        "has_scholarships": True,
        "scholarship_info": "Melbourne International Undergraduate Scholarship 50%. Australia Awards Scholarship (AAS) to'liq.",
        "required_ielts": 6.5,
        "world_ranking": 14,
        "qs_ranking": 14,
        "is_active": True, "is_featured": True,
        "founded_year": 1853,
        "website": "https://unimelb.edu.au",
        "application_url": "https://study.unimelb.edu.au/how-to-apply",
        "application_deadline_fall": date(2025, 10, 31),  # Semester 1 2026: Oct 2025
        "description_uz": "Avstraliya #1. 5 Nobel laureati. Biznes va tibbiyot kuchli.",
    },
]

total_updated = 0
total_created = 0

for data in UNIVERSITIES:
    app_deadline = data.pop('application_deadline_fall', None)
    acceptance   = data.pop('acceptance_rate', None)
    app_url      = data.pop('application_url', None)

    uni, created = University.objects.get_or_create(
        short_name=data['short_name'],
        defaults=data
    )
    if not created:
        for k, v in data.items():
            setattr(uni, k, v)

    if app_deadline: uni.application_deadline_fall = app_deadline
    if acceptance:
        from django.db import models as dm
        if hasattr(uni, 'acceptance_rate'): uni.acceptance_rate = acceptance
    if app_url:
        if hasattr(uni, 'application_url'): uni.application_url = app_url
    uni.save()

    status = "✅ Yangi" if created else "♻️ Yangilandi"
    print(f"  {status}: {uni.name[:50]} | Muddat: {uni.application_deadline_fall}")
    if created: total_created += 1
    else: total_updated += 1

print(f"\n{'='*60}")
print(f"✅ Yangi: {total_created} | ♻️ Yangilandi: {total_updated}")
print(f"📅 Barcha muddatlar 2026-yilga yangilandi!")
print(f"{'='*60}")