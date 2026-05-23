"""Dastlabki ma'lumotlar — universitetlar, fanlar, premium."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.education.models import Subject
from apps.payments.models import PremiumPlan
from apps.universities.models import University, Faculty

print("📚 Fanlar yaratilmoqda...")
subjects = [
    dict(code='math',     name_uz='Matematika',  name_ru='Математика',  name_en='Mathematics',  emoji='🔢', order=1),
    dict(code='english',  name_uz='Ingliz tili', name_ru='Английский',  name_en='English',       emoji='🇬🇧', order=2),
    dict(code='physics',  name_uz='Fizika',       name_ru='Физика',      name_en='Physics',       emoji='⚡', order=3),
    dict(code='chemistry',name_uz='Kimyo',        name_ru='Химия',       name_en='Chemistry',     emoji='🧪', order=4),
    dict(code='biology',  name_uz='Biologiya',    name_ru='Биология',    name_en='Biology',       emoji='🧬', order=5),
    dict(code='history',  name_uz='Tarix',        name_ru='История',     name_en='History',       emoji='📜', order=6),
    dict(code='it',       name_uz='Informatika',  name_ru='Информатика', name_en='IT',            emoji='💻', order=7),
    dict(code='ielts',    name_uz='IELTS',        name_ru='IELTS',       name_en='IELTS',         emoji='📝', order=8),
    dict(code='sat',      name_uz='SAT',          name_ru='SAT',         name_en='SAT',           emoji='🎯', order=9),
]
for s in subjects:
    obj, created = Subject.objects.get_or_create(code=s['code'], defaults={**s, 'is_active': True})
    print(f"  {'✅' if created else '⏭'} {s['name_uz']}")

print("\n💎 Premium rejalar yaratilmoqda...")
plans = [
    dict(name='Oylik Premium', plan_type='monthly', price_usd='9.99', price_uzs='125000',
         duration_days=30, is_active=True,
         features=['Cheksiz AI', 'Mock imtihon', 'Kengaytirilgan statistika', 'VIP universitetlar']),
    dict(name='Yillik Premium', plan_type='yearly', price_usd='79.99', price_uzs='999000',
         duration_days=365, is_active=True,
         features=['Oylik imkoniyatlar', '4 oy bepul', 'Shaxsiy reja', 'Ustun qo\'llab-quvvatlash']),
]
for p in plans:
    obj, created = PremiumPlan.objects.get_or_create(plan_type=p['plan_type'], defaults=p)
    print(f"  {'✅' if created else '⏭'} {p['name']}")

print("\n🏫 Universitetlar yaratilmoqda...")
universities = [
    # O'zbekiston
    dict(name="O'zbekiston Milliy Universiteti", name_uz="O'zbekiston Milliy Universiteti",
         short_name='NUU', country='UZ', city='Toshkent',
         tuition_fee_uzs='4500000', has_scholarships=True,
         dtm_passing_score=180, national_ranking=1, world_ranking=None,
         website='https://nuu.uz', is_active=True, is_featured=True,
         description_uz="O'zbekistonning yetakchi universiteti. Barcha fanlar bo'yicha bakalavriat va magistratura.",
         description_en="Leading university in Uzbekistan."),
    dict(name="Toshkent Davlat Texnika Universiteti", name_uz="Toshkent Davlat Texnika Universiteti",
         short_name='TDTU', country='UZ', city='Toshkent',
         tuition_fee_uzs='5000000', has_scholarships=True,
         dtm_passing_score=170, national_ranking=2,
         website='https://tdtu.uz', is_active=True, is_featured=True,
         description_uz="Texnika va muhandislik bo'yicha O'zbekistonning eng yaxshi universiteti.",
         description_en="Top technical university in Uzbekistan."),
    dict(name="Westminster International University in Tashkent", name_uz="Westminster Xalqaro Universiteti",
         short_name='WIUT', country='UZ', city='Toshkent',
         tuition_fee_usd=4000, has_scholarships=True, scholarship_info="50% gacha chegirma",
         required_ielts='5.5', national_ranking=3,
         website='https://wiut.uz', is_active=True, is_featured=True,
         description_uz="Britaniya standartidagi xalqaro universitet. Ingliz tilida ta'lim.",
         description_en="British-standard international university in Tashkent."),
    dict(name="Inha University in Tashkent", name_uz="Inha Universiteti Toshkentda",
         short_name='INHA', country='UZ', city='Toshkent',
         tuition_fee_usd=3500, has_scholarships=True,
         required_ielts='5.0', national_ranking=4,
         website='https://inha.uz', is_active=True, is_featured=True,
         description_uz="Janubiy Koreya hamkorligidagi universitet. IT va muhandislik yo'nalishlari.",
         description_en="Korean-Uzbek partnership university focused on IT and engineering."),
    dict(name="Turin Polytechnic University in Tashkent", name_uz="Turin Politexnika Universiteti",
         short_name='TTPU', country='UZ', city='Toshkent',
         tuition_fee_usd=4500, has_scholarships=True,
         required_ielts='5.5', national_ranking=5,
         website='https://ttpu.uz', is_active=True,
         description_uz="Italiya texnika universiteti hamkorligi. Muhandislik va arxitektura.",
         description_en="Italian-Uzbek technical university."),
    dict(name="Samarqand Davlat Universiteti", name_uz="Samarqand Davlat Universiteti",
         short_name='SamDU', country='UZ', city='Samarqand',
         tuition_fee_uzs='3800000', has_scholarships=True,
         dtm_passing_score=160, national_ranking=6,
         website='https://samdu.uz', is_active=True,
         description_uz="Samarqanddagi yetakchi davlat universiteti.",
         description_en="Leading state university in Samarkand."),

    # USA
    dict(name="Massachusetts Institute of Technology", name_uz="MIT",
         short_name='MIT', country='US', city='Cambridge',
         tuition_fee_usd=57986, has_scholarships=True,
         scholarship_info="Need-based scholarship, to'liq qoplashi mumkin",
         required_ielts='7.0', required_sat=1500, world_ranking=1,
         website='https://mit.edu', application_deadline_fall='2024-01-01',
         is_active=True, is_featured=True,
         description_uz="Dunyodagi eng yaxshi texnika universiteti. Ilm-fan va innovatsiya markazi.",
         description_en="World's top technical university."),
    dict(name="Harvard University", name_uz="Harvard Universiteti",
         short_name='Harvard', country='US', city='Cambridge',
         tuition_fee_usd=59950, has_scholarships=True,
         scholarship_info="Need-blind admission, to'liq moliyaviy yordam",
         required_ielts='7.0', required_sat=1580, world_ranking=3,
         website='https://harvard.edu', application_deadline_fall='2024-01-01',
         is_active=True, is_featured=True,
         description_uz="Dunyoning eng nufuzli universiteti. 1636-yilda tashkil etilgan.",
         description_en="World's most prestigious university, founded in 1636."),
    dict(name="Stanford University", name_uz="Stenford Universiteti",
         short_name='Stanford', country='US', city='Stanford',
         tuition_fee_usd=56169, has_scholarships=True,
         required_ielts='7.0', required_sat=1570, world_ranking=5,
         website='https://stanford.edu', is_active=True,
         description_uz="Silicon Valley qalbida joylashgan innovatsiya universiteti.",
         description_en="Innovation university in the heart of Silicon Valley."),

    # UK
    dict(name="University of Oxford", name_uz="Oksford Universiteti",
         short_name='Oxford', country='GB', city='Oxford',
         tuition_fee_usd=35000, has_scholarships=True,
         scholarship_info="Rhodes Scholarship, Clarendon Fund",
         required_ielts='7.5', world_ranking=2,
         website='https://ox.ac.uk', is_active=True, is_featured=True,
         description_uz="Dunyo tariхidagi eng qadimiy universitetlardan biri. 1096-yilda tashkil etilgan.",
         description_en="One of the oldest universities in the world."),
    dict(name="University of Cambridge", name_uz="Kembrij Universiteti",
         short_name='Cambridge', country='GB', city='Cambridge',
         tuition_fee_usd=33000, has_scholarships=True,
         required_ielts='7.5', world_ranking=4,
         website='https://cam.ac.uk', is_active=True,
         description_uz="Oksford bilan birga Britaniyaning eng nufuzli universiteti.",
         description_en="One of the world's most prestigious universities."),
    dict(name="Imperial College London", name_uz="Imperial Kollej London",
         short_name='ICL', country='GB', city='London',
         tuition_fee_usd=32000, has_scholarships=True,
         required_ielts='6.5', world_ranking=8,
         website='https://imperial.ac.uk', is_active=True,
         description_uz="Fan va texnologiya bo'yicha Britaniyaning top universiteti.",
         description_en="UK's top science and technology university."),

    # Germany
    dict(name="Technical University of Munich", name_uz="Myunxen Texnika Universiteti",
         short_name='TUM', country='DE', city='Munich',
         tuition_fee_usd=500, has_scholarships=True,
         scholarship_info="DAAD stipendiyasi — oyiga 850 EUR",
         required_ielts='6.5', world_ranking=30,
         website='https://tum.de', is_active=True, is_featured=True,
         description_uz="Germaniyaning eng yaxshi texnika universiteti. Aksariyat dasturlar bepul!",
         description_en="Germany's top technical university. Most programs are free!"),
    dict(name="Heidelberg University", name_uz="Xaydelberk Universiteti",
         short_name='Heidelberg', country='DE', city='Heidelberg',
         tuition_fee_usd=200, has_scholarships=True,
         required_ielts='6.0', world_ranking=45,
         website='https://uni-heidelberg.de', is_active=True,
         description_uz="Germaniyaning eng qadimiy universiteti. Tibbiyot va tabiiy fanlar.",
         description_en="Germany's oldest university, renowned for medicine and natural sciences."),

    # South Korea
    dict(name="Seoul National University", name_uz="Seul Milliy Universiteti",
         short_name='SNU', country='KR', city='Seoul',
         tuition_fee_usd=4500, has_scholarships=True,
         scholarship_info="GKS (Korean Government Scholarship) — to'liq moliyaviy",
         required_ielts='6.0', required_toefl=83, world_ranking=35,
         website='https://snu.ac.kr', is_active=True, is_featured=True,
         description_uz="Koreya Respublikasining eng prestijli universiteti. Hukumat stipendiyasi bor.",
         description_en="South Korea's most prestigious university with government scholarships."),
    dict(name="KAIST", name_uz="KAIST",
         short_name='KAIST', country='KR', city='Daejeon',
         tuition_fee_usd=3000, has_scholarships=True,
         scholarship_info="KAIST Fellowship — to'liq stipendiya",
         required_ielts='6.0', world_ranking=55,
         website='https://kaist.ac.kr', is_active=True,
         description_uz="Koreya ilm-fan va texnologiya instituti. IT va muhandislik.",
         description_en="Korea Advanced Institute of Science and Technology."),

    # Turkey
    dict(name="Middle East Technical University", name_uz="O'rta Sharq Texnika Universiteti",
         short_name='METU', country='TR', city='Ankara',
         tuition_fee_usd=600, has_scholarships=True,
         scholarship_info="Turkiya Burslari — to'liq moliyaviy yordam",
         required_ielts='6.0', world_ranking=401,
         website='https://metu.edu.tr', is_active=True, is_featured=True,
         description_uz="Turk universitetlari ichida eng yuqori reytingda. Ingliz tilida ta'lim.",
         description_en="Turkey's highest-ranked university with English instruction."),
    dict(name="Istanbul Technical University", name_uz="Istanbul Texnika Universiteti",
         short_name='ITU', country='TR', city='Istanbul',
         tuition_fee_usd=400, has_scholarships=True,
         required_ielts='5.5', world_ranking=501,
         website='https://itu.edu.tr', is_active=True,
         description_uz="Dunyo universitetlari ichida eng qadimiy texnika universitetlaridan biri.",
         description_en="One of the oldest technical universities in the world."),

    # Russia
    dict(name="Moscow State University", name_uz="Moskva Davlat Universiteti",
         short_name='MGU', country='RU', city='Moscow',
         tuition_fee_usd=4000, has_scholarships=True,
         scholarship_info="Rossiya hukumati kvotasi — bepul o'qish",
         required_ielts=None, world_ranking=74,
         website='https://msu.ru', is_active=True,
         description_uz="Rossiyaning eng nufuzli universiteti. Hukumat kvotasi bo'yicha bepul o'qish mumkin.",
         description_en="Russia's most prestigious university."),

    # China
    dict(name="Tsinghua University", name_uz="Sinxua Universiteti",
         short_name='THU', country='CN', city='Beijing',
         tuition_fee_usd=4500, has_scholarships=True,
         scholarship_info="CSC Scholarship — Xitoy hukumati stipendiyasi",
         required_ielts='6.5', world_ranking=14,
         website='https://tsinghua.edu.cn', is_active=True,
         description_uz="Xitoyning eng yaxshi universiteti. Kuchli stipendiya dasturi mavjud.",
         description_en="China's top university with strong scholarship programs."),

    # Malaysia
    dict(name="University of Malaya", name_uz="Malayziya Universiteti",
         short_name='UM', country='MY', city='Kuala Lumpur',
         tuition_fee_usd=3500, has_scholarships=True,
         required_ielts='6.0', world_ranking=65,
         website='https://um.edu.my', is_active=True,
         description_uz="Janubi-Sharqiy Osiyodagi eng yaxshi universitetlardan biri. Qulay narxlar.",
         description_en="One of the best universities in Southeast Asia."),
]

created_count = 0
for data in universities:
    obj, created = University.objects.get_or_create(name=data['name'], defaults=data)
    if created:
        created_count += 1
        print(f"  ✅ {data['name']}")
    else:
        # Ma'lumotlarni yangilash
        for k, v in data.items():
            if v is not None:
                setattr(obj, k, v)
        obj.save()
        print(f"  ♻️  {data['name']} (yangilandi)")

print(f"\n✅ Jami {created_count} ta yangi universitet qo'shildi!")
print(f"📊 Bazada jami: {University.objects.count()} ta universitet")
print("\n🎉 Barcha dastlabki ma'lumotlar tayyor!")
