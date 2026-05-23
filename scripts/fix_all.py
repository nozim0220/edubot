"""Hamma muammolarni tuzatish — bir skript."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User
from apps.education.models import Subject, Question, Test, TestQuestion
from apps.universities.models import University, Faculty
from apps.payments.models import PremiumPlan

print("=" * 55)
print("  EduBot — To'liq ma'lumotlar yangilash")
print("=" * 55)

# ── 1. BARCHA USERLARNI ADMIN QILISH IMKONIYATI ──────
print("\n👥 Foydalanuvchilar:")
users = list(User.objects.all())
if not users:
    print("  Hech qanday foydalanuvchi yo'q. Bot orqali /start bosing.")
else:
    for u in users:
        admin_mark = "👑 ADMIN" if (u.is_admin or u.is_staff) else ""
        print(f"  {u.telegram_id} | {u.full_name} {admin_mark}")
    
    print()
    tg_id = input("Admin qilmoqchi telegram_id (bo'sh qoldirsa hammani): ").strip()
    if tg_id:
        try:
            target = User.objects.get(telegram_id=int(tg_id))
            target.is_admin = True
            target.is_staff = True
            target.save(update_fields=['is_admin','is_staff'])
            print(f"  ✅ {target.full_name} — ADMIN qilindi!")
        except Exception as e:
            print(f"  ❌ {e}")
    else:
        User.objects.all().update(is_admin=True, is_staff=True)
        print("  ✅ Hamma foydalanuvchilar admin qilindi!")

# ── 2. SAVOLLAR QO'SHISH ──────────────────────────────
print("\n❓ Savollar qo'shilmoqda...")

questions_data = {
    'math': [
        ("2 + 2 × 2 = ?", "4", "6", "8", "10", "B", "Avval ko'paytma: 2×2=4, keyin: 2+4=6", "easy"),
        ("log₂(32) = ?", "4", "5", "6", "8", "B", "2⁵=32, shuning uchun log₂(32)=5", "medium"),
        ("sin(30°) = ?", "1", "√3/2", "1/2", "0", "C", "sin(30°)=1/2 — standart qiymat", "easy"),
        ("(a+b)² nima?", "a²+b²", "a²+2ab+b²", "a²-2ab+b²", "2(a+b)", "B", "(a+b)²=a²+2ab+b²", "easy"),
        ("10 sonning o'rtachasi 15, yig'indisi:", "25", "100", "150", "200", "C", "15×10=150", "easy"),
        ("2ˣ = 16 bo'lsa, x = ?", "2", "3", "4", "8", "C", "2⁴=16", "easy"),
        ("3² + 4² = ?", "14", "25", "49", "7", "B", "9+16=25", "easy"),
        ("Uchburchak tomonlari 3,4,5. Gipotenuza:", "3", "4", "5", "7", "C", "√(9+16)=5", "medium"),
        ("f(x)=2x²+3x-5, f(2)=?", "9", "10", "11", "12", "A", "8+6-5=9", "medium"),
        ("√144 = ?", "11", "12", "13", "14", "B", "12²=144", "easy"),
        ("15% of 200 = ?", "20", "25", "30", "35", "C", "200×0.15=30", "easy"),
        ("Agar 3x-9=0, x=?", "1", "2", "3", "4", "C", "3x=9, x=3", "easy"),
        ("0.5² = ?", "0.1", "0.25", "0.5", "1", "B", "0.5×0.5=0.25", "easy"),
        ("1+2+3+...+10 = ?", "45", "50", "55", "60", "C", "n(n+1)/2=10×11/2=55", "medium"),
        ("cos(0°) = ?", "0", "1/2", "√3/2", "1", "D", "cos(0°)=1", "easy"),
        ("2³ × 2² = ?", "2⁵", "2⁶", "4⁵", "6²", "A", "2^(3+2)=2⁵=32", "medium"),
        ("|-7| = ?", "-7", "7", "0", "49", "B", "Absolut qiymat musbat", "easy"),
        ("Doira yuzi (r=5):", "25π", "10π", "5π", "50π", "A", "πr²=25π", "medium"),
        ("Tenglik: 7x=35, x=?", "4", "5", "6", "7", "B", "x=35/7=5", "easy"),
        ("1000 ning 1% = ?", "1", "10", "100", "0.1", "B", "1000×0.01=10", "easy"),
    ],
    'english': [
        ("She _____ here since 2020.", "lives", "lived", "has lived", "is living", "C", "Present perfect: since bilan ishlatiladi", "medium"),
        ("He _____ TV when I called.", "watched", "was watching", "has watched", "watches", "B", "Past continuous: o'sha paytda davom etayotgan harakat", "medium"),
        ("'Pristine' means:", "Old", "Dirty", "Perfectly clean", "Broken", "C", "Pristine = perfectly clean or new", "medium"),
        ("If I _____ you, I'd study harder.", "am", "was", "were", "will be", "C", "2nd conditional: If I were you", "hard"),
        ("The book _____ by Tolstoy.", "wrote", "written", "was written", "has written", "C", "Passive voice: was written", "medium"),
        ("Choose correct: He don't / doesn't like it.", "don't", "doesn't", "do not", "does not like", "B", "He/She/It + doesn't (3rd person singular)", "easy"),
        ("Plural of 'child':", "childs", "childes", "children", "child's", "C", "Irregular plural: child → children", "easy"),
        ("'Enormous' is closest to:", "Tiny", "Huge", "Normal", "Strange", "B", "Enormous = very large/huge", "easy"),
        ("She asked me where ___ from.", "I came", "did I come", "I come", "come I", "A", "Indirect question: normal word order", "hard"),
        ("Past tense of 'buy':", "buyed", "boughted", "bought", "buys", "C", "Irregular verb: buy → bought", "easy"),
        ("They _____ the project by Friday.", "finish", "will finish", "will have finished", "finished", "C", "Future perfect: action completed before future point", "hard"),
        ("'Quickly' is a/an:", "Noun", "Verb", "Adjective", "Adverb", "D", "-ly qo'shimchali so'z adverb (ravish)", "easy"),
        ("Correct sentence:", "I have went", "I has gone", "I have gone", "I gone", "C", "Present perfect: have/has + past participle", "medium"),
        ("'Abandon' means:", "Find", "Keep", "Leave behind", "Start", "C", "Abandon = leave permanently", "medium"),
        ("Neither A nor B _____ correct.", "are", "is", "were", "be", "B", "Neither...nor + singular verb", "hard"),
        ("Superlative of 'good':", "gooder", "better", "goodest", "best", "D", "Irregular: good → better → best", "easy"),
        ("'Although' is used for:", "Reason", "Result", "Contrast", "Addition", "C", "Although = despite the fact that (contrast)", "medium"),
        ("I wish I _____ speak French.", "can", "could", "will", "would", "B", "Wish + past tense: could", "hard"),
        ("'Investigate' means:", "Ignore", "Examine carefully", "Destroy", "Build", "B", "Investigate = examine systematically", "medium"),
        ("He's been working here _____ 5 years.", "since", "for", "ago", "during", "B", "for = duration bilan, since = point in time bilan", "easy"),
    ],
    'physics': [
        ("F = m × a — bu qaysi qonun?", "1-qonun", "2-qonun", "3-qonun", "Energiya qonuni", "B", "Nyutonning 2-qonuni: F=ma", "easy"),
        ("Yorug'lik tezligi (vakuumda):", "3×10⁶", "3×10⁸", "3×10¹⁰", "3×10⁴", "B", "c=3×10⁸ m/s", "easy"),
        ("Og'irlik kuchi g=?", "8.9", "9.8", "10.8", "11", "B", "g≈9.8 m/s²", "easy"),
        ("Issiqlik Q=?", "mcT", "mc/T", "m+c", "c/mT", "A", "Q=mcΔT", "medium"),
        ("Ohm qonuni I=?", "R/U", "U×R", "U/R", "R-U", "C", "I=U/R", "easy"),
        ("Quvvat P=?", "I/U", "U/I", "U×I", "U+I", "C", "P=UI (Vatt)", "easy"),
        ("Kinetik energiya Ek=?", "mv", "mv²", "mv²/2", "2mv²", "C", "Ek=mv²/2", "medium"),
        ("Potensial energiya Ep=?", "mgh", "mg/h", "m+g+h", "mh/g", "A", "Ep=mgh", "easy"),
        ("1 Joule = ?", "1 N×m", "1 kg×m", "1 W×s²", "1 N/m", "A", "Joule = Newton × metr", "medium"),
        ("Boyle qonuni: P₁V₁=P₂V₂ (T=const) — bu:", "Izobarik", "Izotermik", "Izoxorik", "Adiabatik", "B", "T=const — izotermik jarayon", "hard"),
        ("Nyuton 1-qonuni nima deydi?", "F=ma", "Inersiya qonuni", "Harakat miqdori", "Energiya saqlanishi", "B", "Inersiya: kuch bo'lmasa jism holatini o'zgartirmaydi", "easy"),
        ("Elektr zaryad birligi:", "Amper", "Volt", "Kulon", "Om", "C", "Zaryad birligi — Kulon (C)", "easy"),
        ("Transformer nima uchun?", "Tezlik o'zgartirish", "Kuchlanish o'zgartirish", "Tok kuchi o'zgartirish", "Energiya saqlash", "B", "Transformator kuchlanishni o'zgartiradi", "medium"),
        ("Rezonans nima?", "Tebranish to'xtashi", "Tebranish amplitudasi max", "Tebranish davri 0", "Tezlik max", "B", "Rezonans: tashqi kuch chastotasi = tabiiy chastota", "hard"),
        ("1 kWh = ? J", "3.6×10³", "3.6×10⁶", "3.6×10⁹", "360", "B", "1 kWh = 3600000 J = 3.6×10⁶ J", "hard"),
    ],
    'chemistry': [
        ("Suv formulasi:", "CO₂", "H₂O", "NaCl", "O₂", "B", "H₂O — 2 vodorod, 1 kislorod", "easy"),
        ("Osh tuzi:", "KCl", "CaCO₃", "NaCl", "MgO", "C", "NaCl — natriy xlorid", "easy"),
        ("Eng yengil element:", "Geliy", "Litiy", "Vodorod", "Neon", "C", "H, atom massasi=1", "easy"),
        ("pH=7:", "Kislotali", "Neytral", "Ishqoriy", "Tuzli", "B", "pH 7 = neytral muhit", "easy"),
        ("CO₂:", "Kislorod", "Azot", "Karbonat angidrid", "Vodorod", "C", "Carbon dioxide", "easy"),
        ("Valentlik nima?", "Atomlar soni", "Bog' hosil qilish qobiliyati", "Massa", "Zaryad", "B", "Valentlik — atom hosil qiladigan kimyoviy bog'lar soni", "medium"),
        ("Kislota + Ishqor = ?", "Tuz", "Tuz + Suv", "Suv", "Gaz", "B", "Neytrallanish: Kislota + Ishqor → Tuz + H₂O", "easy"),
        ("Mendeleev jadvali nima?", "Elementlar tasnifi", "Reaksiyalar ro'yxati", "Izotoplar jadvali", "Oksidlanish darajalari", "A", "Davriy sistema — elementlarni tartibga soladi", "easy"),
        ("Eng ko'p tarqalgan element (yer qobig'i):", "Temir", "Alyuminiy", "Kislorod", "Kremniy", "C", "Kislorod — yer qobig'ining ~46%", "medium"),
        ("Organik kimyo nimani o'rganadi?", "Metallar", "Uglerod birikmalar", "Tuzlar", "Gazlar", "B", "Organik kimyo — C asosidagi birikmalar", "easy"),
        ("H₂SO₄ nima?", "Xlorid kislota", "Sulfat kislota", "Nitrat kislota", "Fosfor kislota", "B", "H₂SO₄ = sulfat kislota", "easy"),
        ("Polimer nima?", "Oddiy molekula", "Ko'p takrorlanuvchi zanjir", "Ion", "Atom", "B", "Polimer = takrorlanuvchi monomerlar zanjiri", "medium"),
        ("Elektroliz nima?", "Issiqlik bilan parchalanish", "Elektr toki bilan parchalanish", "Yorug'lik bilan parchalanish", "Mexanik parchalanish", "B", "Elektroliz — elektr toki orqali kimyoviy reaksiya", "medium"),
        ("NaOH nima?", "Kislota", "Neytral tuz", "Ishqor", "Oksid", "C", "NaOH = natriy gidroksid (ishqor)", "easy"),
        ("Oksidlanish — bu:", "Elektron qo'shish", "Elektron berish", "Proton qo'shish", "Neytron berish", "B", "Oksidlanish = elektronlar yo'qotish", "hard"),
    ],
    'biology': [
        ("DNK = ?", "Dezoksiribonuklein kislota", "Ribonuklein kislota", "Aminokislota", "Glyukoza", "A", "Deoxyribonucleic Acid", "easy"),
        ("Hujayra 'batareyasi':", "Yadro", "Mitoxondriya", "Ribosoma", "Lizosoma", "B", "Mitoxondriya ATP ishlab chiqaradi", "easy"),
        ("Fotosintez joyi:", "Mitoxondriya", "Yadro", "Xloroplast", "Ribosoma", "C", "Xlorofill xloroplastda", "easy"),
        ("Eng katta organ:", "Jigar", "Teri", "O'pka", "Miya", "B", "Teri ~1.5-2 m²", "easy"),
        ("Qon guruhlari:", "2", "3", "4", "5", "C", "I(O), II(A), III(B), IV(AB)", "easy"),
        ("Evoluysiya nazariyasi:", "Mendel", "Darvin", "Pasteur", "Flemming", "B", "Charlz Darvin, 1859", "easy"),
        ("Oqsil sintezi joyi:", "Yadro", "Xloroplast", "Ribosoma", "Mitoxondriya", "C", "Ribosoma — mRNA asosida", "easy"),
        ("Fotosintez formulasi:", "CO₂+H₂O→C₆H₁₂O₆+O₂", "O₂+H₂O→CO₂", "C₆H₁₂O₆→CO₂+H₂O", "H₂O→H₂+O", "A", "6CO₂+6H₂O+nur→C₆H₁₂O₆+6O₂", "medium"),
        ("Mitoz nima?", "Jinsiy ko'payish", "Yadrosiz bo'linish", "Bir xil 2 ta hujayra", "Spor hosil qilish", "C", "Mitoz = bir xil 2 ta diploid hujayra hosil qiladi", "medium"),
        ("Insulin qayerda ishlab chiqariladi?", "Jigar", "Oshqozon osti bezi", "Buyrak usti", "Qalqonsimon", "B", "Insulin — Langergans orolchalari (me'da osti bezi)", "medium"),
        ("Xromosomalar soni (inson):", "23", "46", "48", "44", "B", "46 ta xromosoma (23 juft)", "easy"),
        ("ATP nima?", "Yog'", "Oqsil", "Energiya molekulasi", "DNK", "C", "Adenozin trifosfat — energiya 'valyutasi'", "easy"),
        ("Virus — tirik organizm?", "Ha", "Yo'q", "Ba'zan", "Faqat hayvonda", "B", "Virus — hujayrasiz, tirik emas", "medium"),
        ("Meyoz natijasi:", "2 ta diploid", "4 ta haploid", "2 ta haploid", "4 ta diploid", "B", "Meyoz = 4 ta haploid hujayra (jinsiy hujayralar)", "hard"),
        ("Reflektor yoy:", "Reseptor→effektor", "Reseptor→nerv→effektor", "Miya→muskul", "Qon→nerv", "B", "Reseptor→afferent nerv→markaziy NS→efferent nerv→effektor", "hard"),
    ],
    'history': [
        ("O'zbekiston mustaqilligi:", "1990", "1991", "1992", "1993", "B", "1991-yil 1-sentabr", "easy"),
        ("Amir Temur tug'ilgan yil:", "1336", "1370", "1405", "1300", "A", "1336-yil, Shahrisabz", "easy"),
        ("1-jahon urushi boshlanishi:", "1912", "1913", "1914", "1915", "C", "1914-yil 28-iyul", "easy"),
        ("Buyuk Ipak yo'li yo'nalishi:", "Xitoydan Yevropaga", "Hindistondan Afrikaga", "Arabistondan Xitoyga", "Rossiyadan Hindistonga", "A", "Sharqdan G'arbga", "easy"),
        ("Ulug'bek rasadxonasi:", "Buxoro", "Xiva", "Samarqand", "Toshkent", "C", "Samarqand, 1428-1429", "easy"),
        ("2-jahon urushi tugashi:", "1944", "1945", "1946", "1947", "B", "1945-yil 2-sentabr", "easy"),
        ("Al-Xorazmiy sohasi:", "Tibbiyot", "Astronomiya", "Matematika", "Kimyo", "C", "Algebra asosini yaratdi", "easy"),
        ("Islom Karimov — O'zbekiston prezidenti nechanchi yilgacha?", "2010", "2016", "2017", "2015", "B", "2016-yil 2-sentabrda vafot etdi", "medium"),
        ("Temuriylar davlati poytaxti:", "Buxoro", "Xiva", "Samarqand", "Toshkent", "C", "Amir Temur Samarqandni poytaxt qildi", "easy"),
        ("Birinchi kosmonaut:", "Nil Armstrong", "Yuriy Gagarin", "Valentin Terashkova", "Alan Shepard", "B", "Gagarin, 1961-yil 12-aprel", "easy"),
        ("Fransuz inqilobi yili:", "1776", "1789", "1800", "1812", "B", "1789-yil 14-iyul — Bastiliya qal'asi bosib olinishi", "medium"),
        ("Ikkinchi jahon urushini kim boshlatdi?", "Yaponiya", "Italiya", "Germaniya (Gitler)", "SSSR", "C", "1939-yil 1-sentabr Polshaga hujum", "easy"),
        ("Al-Beruniy qayerda tug'ilgan?", "Buxoro", "Samarqand", "Xorazm (Kath)", "Termiz", "C", "973-yil, Xorazm (hozirgi Beruniy sh.)", "medium"),
        ("Xitoy Buyuk devori qachon qurilgan?", "Mil. av. 7-asr", "Mil. av. 3-asr", "1-asr", "5-asr", "B", "Qin sulolasi, mil.av. 221-yil asosan", "hard"),
        ("O'zbekistonda birinchi prezident:", "Shavkat Mirziyoyev", "Islom Karimov", "Nishonov", "Rahimov", "B", "Islom Karimov (1991-2016)", "easy"),
    ],
    'it': [
        ("HTML nima?", "Dasturlash tili", "Belgilash tili", "Ma'lumotlar bazasi", "OS", "B", "HyperText Markup Language", "easy"),
        ("CPU = ?", "Xotira", "Grafik protsessor", "Markaziy protsessor", "Tarmoq kartasi", "C", "Central Processing Unit", "easy"),
        ("1 GB = ?", "1000 MB", "1024 MB", "512 MB", "2048 MB", "B", "Ikkilik sistema", "easy"),
        ("Python turi:", "Kompilyatsiya", "Interpretatsiya", "Assembler", "Mashina", "B", "Interpreted high-level language", "easy"),
        ("SQL nima uchun?", "Veb-dizayn", "Ma'lumotlar bazasi", "Tarmoq", "Grafika", "B", "Structured Query Language", "easy"),
        ("1010₂ = ?", "8", "10", "12", "14", "B", "1×8+0×4+1×2+0=10", "easy"),
        ("OOP nima?", "Open Protocol", "Object-Oriented Programming", "Output Program", "Online Parsing", "B", "Ob'ektga yo'naltirilgan dasturlash", "easy"),
        ("HTTP nima?", "Fayl tizimi", "Veb protokoli", "Dasturlash tili", "Xavfsizlik", "B", "HyperText Transfer Protocol", "easy"),
        ("for loop nima?", "Shartli operator", "Takrorlash operatori", "Funksiya", "Sinf", "B", "Takrorlash uchun tsikl", "easy"),
        ("Git nima?", "Dasturlash tili", "Versiya boshqaruvi", "Veb server", "Ma'lumotlar bazasi", "B", "Distributed version control system", "easy"),
        ("RAM va ROM farqi:", "RAM o'chmas, ROM o'chuvchan", "RAM o'chuvchan, ROM o'chmas", "Ikkalasi bir xil", "ROM tezroq", "B", "RAM=operativ (o'chuvchan), ROM=doimiy", "medium"),
        ("API nima?", "Dastur interfeysi", "Dasturlar o'rtasida aloqa", "Veb-sayt", "Ma'lumotlar bazasi", "B", "Application Programming Interface", "medium"),
        ("Firewall nima?", "Zaxira", "Tarmoq xavfsizlik tizimi", "Processor", "Monitor", "B", "Tarmoqqa kirishni filtrlaydi", "medium"),
        ("CSS nima uchun?", "Mantiq", "Uslub/dizayn", "Ma'lumotlar bazasi", "Server", "B", "Cascading Style Sheets — veb-sahifa ko'rinishi", "easy"),
        ("Algoritm nima?", "Dasturlash tili", "Muammoni hal qilish qadamlari", "Kompyuter", "Kod", "B", "Muammo yechimi uchun aniq qadamlar to'plami", "easy"),
    ],
}

total_added = 0
for code, q_list in questions_data.items():
    try:
        subj = Subject.objects.get(code=code)
    except Subject.DoesNotExist:
        print(f"  ⚠️  Subject '{code}' topilmadi, o'tkazildi")
        continue
    
    existing = Question.objects.filter(subject=subj).count()
    added = 0
    for q_data in q_list:
        text, a, b, c, d, ans, exp, diff = q_data
        if not Question.objects.filter(subject=subj, text_uz=text).exists():
            Question.objects.create(
                subject=subj, text_uz=text,
                option_a=a, option_b=b, option_c=c, option_d=d,
                correct_answer=ans, explanation_uz=exp,
                difficulty=diff, is_active=True, xp_reward=10,
            )
            added += 1
    print(f"  ✅ {subj.name_uz}: {added} ta yangi savol ({existing+added} jami)")
    total_added += added

print(f"\n📊 Jami {total_added} ta savol qo'shildi!")

# ── 3. TESTLAR YARATISH ───────────────────────────────
print("\n🎯 Testlar yaratilmoqda...")
for code in questions_data.keys():
    try:
        subj = Subject.objects.get(code=code)
    except Subject.DoesNotExist:
        continue
    
    qs = list(Question.objects.filter(subject=subj, is_active=True)[:10])
    if not qs:
        continue
    
    test, created = Test.objects.get_or_create(
        subject=subj, test_type='quiz',
        defaults={'title_uz': f"{subj.name_uz} — Test", 'passing_score': 60, 'is_active': True}
    )
    if created:
        for i, q in enumerate(qs):
            TestQuestion.objects.get_or_create(test=test, question=q, defaults={'order': i})
        print(f"  ✅ {subj.name_uz} test yaratildi ({len(qs)} savol)")
    else:
        print(f"  ⏭  {subj.name_uz} test mavjud")

# ── 4. FAKULTETLAR QO'SHISH ───────────────────────────
print("\n🎓 Fakultetlar qo'shilmoqda...")

faculties_data = {
    "O'zbekiston Milliy Universiteti": [
        ("Matematika va informatika", "Amaliy matematika", "Bachelor", 4, None, "O'zbek/Rus"),
        ("Fizika", "Nazariy fizika", "Bachelor", 4, None, "O'zbek"),
        ("Kimyo", "Kimyo", "Bachelor", 4, None, "O'zbek"),
        ("Biologiya", "Biologiya", "Bachelor", 4, None, "O'zbek"),
        ("Tarix", "Tarix", "Bachelor", 4, None, "O'zbek"),
        ("Filologiya", "O'zbek tili va adabiyoti", "Bachelor", 4, None, "O'zbek"),
        ("Xalqaro munosabatlar", "Xalqaro munosabatlar", "Bachelor", 4, None, "O'zbek/Rus"),
    ],
    "Toshkent Davlat Texnika Universiteti": [
        ("Muhandislik", "Sanoat muhandisligi", "Bachelor", 4, None, "O'zbek/Rus"),
        ("Kompyuter muhandisligi", "Dasturiy injiniring", "Bachelor", 4, None, "O'zbek"),
        ("Mexanika", "Mexanika va konstruksiya", "Bachelor", 4, None, "O'zbek"),
        ("Energetika", "Elektr energetika", "Bachelor", 4, None, "O'zbek"),
        ("Qurilish", "Qurilish va arxitektura", "Bachelor", 4, None, "O'zbek"),
    ],
    "Westminster International University in Tashkent": [
        ("Biznes va iqtisodiyot", "Biznes boshqaruvi", "Bachelor", 3, 4000, "English"),
        ("Biznes va iqtisodiyot", "Moliya va bank ishi", "Bachelor", 3, 4000, "English"),
        ("Kompyuter fanlari", "Dasturiy ta'minot muhandisligi", "Bachelor", 3, 4500, "English"),
        ("Kompyuter fanlari", "Kiber xavfsizlik", "Bachelor", 3, 4500, "English"),
        ("Huquq", "Huquq (LLB)", "Bachelor", 3, 4000, "English"),
    ],
    "Inha University in Tashkent": [
        ("Elektr muhandisligi", "Elektr va elektronika", "Bachelor", 4, 3500, "English/Korean"),
        ("Kompyuter fanlari", "Kompyuter fanlari", "Bachelor", 4, 3500, "English"),
        ("Mexanika", "Mexanik muhandislik", "Bachelor", 4, 3500, "English"),
        ("Sanoat muhandisligi", "Sanoat va tizim muhandisligi", "Bachelor", 4, 3500, "English"),
    ],
    "Massachusetts Institute of Technology": [
        ("Engineering", "Computer Science & Engineering", "Bachelor", 4, 57986, "English"),
        ("Engineering", "Electrical Engineering", "Bachelor", 4, 57986, "English"),
        ("Science", "Mathematics", "Bachelor", 4, 57986, "English"),
        ("Science", "Physics", "Bachelor", 4, 57986, "English"),
        ("Management", "Business Analytics", "Master", 2, 77170, "English"),
        ("Architecture", "Architecture & Design", "Bachelor", 4, 57986, "English"),
    ],
    "Harvard University": [
        ("Liberal Arts", "Economics", "Bachelor", 4, 59950, "English"),
        ("Liberal Arts", "Political Science", "Bachelor", 4, 59950, "English"),
        ("Law School", "Juris Doctor (JD)", "Master", 3, 67081, "English"),
        ("Business School", "MBA", "Master", 2, 73440, "English"),
        ("Medical School", "Doctor of Medicine (MD)", "Doctoral", 4, 65000, "English"),
        ("Science", "Computer Science", "Bachelor", 4, 59950, "English"),
    ],
    "University of Oxford": [
        ("Humanities", "Philosophy, Politics & Economics (PPE)", "Bachelor", 3, 35000, "English"),
        ("Science", "Mathematics", "Bachelor", 3, 35000, "English"),
        ("Science", "Computer Science", "Bachelor", 3, 35000, "English"),
        ("Medicine", "Medicine (MBBCh)", "Bachelor", 6, 38000, "English"),
        ("Business", "MBA (Said Business School)", "Master", 1, 62000, "English"),
        ("Law", "Bachelor of Civil Law", "Master", 1, 35000, "English"),
    ],
    "Technical University of Munich": [
        ("Informatik", "Computer Science (Informatik)", "Bachelor", 3, 500, "German/English"),
        ("Engineering", "Mechanical Engineering", "Bachelor", 3, 500, "German/English"),
        ("Engineering", "Electrical Engineering", "Bachelor", 3, 500, "German"),
        ("Natural Sciences", "Mathematics", "Bachelor", 3, 500, "German"),
        ("Management", "MBA TUM", "Master", 2, 15000, "English"),
        ("Architecture", "Architecture", "Bachelor", 4, 500, "German"),
    ],
    "Seoul National University": [
        ("Engineering", "Computer Science & Engineering", "Bachelor", 4, 4500, "Korean/English"),
        ("Natural Sciences", "Physics", "Bachelor", 4, 3500, "Korean"),
        ("Business", "Business Administration", "Bachelor", 4, 4000, "Korean/English"),
        ("Medicine", "Medicine", "Bachelor", 6, 5000, "Korean"),
        ("Law", "Law School (JD)", "Master", 3, 5500, "Korean"),
        ("Engineering", "Electrical Engineering", "Bachelor", 4, 4500, "Korean/English"),
    ],
    "Middle East Technical University": [
        ("Engineering", "Computer Engineering", "Bachelor", 4, 600, "English"),
        ("Engineering", "Industrial Engineering", "Bachelor", 4, 600, "English"),
        ("Science", "Physics", "Bachelor", 4, 600, "English"),
        ("Architecture", "Architecture", "Bachelor", 4, 600, "English"),
        ("Business", "Business Administration", "Bachelor", 4, 600, "English"),
    ],
    "Tsinghua University": [
        ("Engineering", "Computer Science", "Bachelor", 4, 4500, "Chinese/English"),
        ("Engineering", "Electrical Engineering", "Bachelor", 4, 4000, "Chinese"),
        ("Science", "Mathematics", "Bachelor", 4, 3500, "Chinese"),
        ("Economics", "Economics & Management", "Bachelor", 4, 4500, "Chinese/English"),
        ("Medicine", "Clinical Medicine", "Bachelor", 5, 5000, "Chinese"),
    ],
    "University of Malaya": [
        ("Engineering", "Computer System & Network", "Bachelor", 4, 3500, "English"),
        ("Science", "Mathematics", "Bachelor", 3, 3000, "English"),
        ("Business", "Business Administration", "Bachelor", 3, 3200, "English"),
        ("Medicine", "Medicine (MBBS)", "Bachelor", 5, 8000, "English"),
        ("Engineering", "Electrical Engineering", "Bachelor", 4, 3500, "English"),
    ],
    "Samarqand Davlat Universiteti": [
        ("Tarix", "Tarix", "Bachelor", 4, None, "O'zbek"),
        ("Filologiya", "O'zbek tili", "Bachelor", 4, None, "O'zbek"),
        ("Matematika", "Matematika", "Bachelor", 4, None, "O'zbek"),
        ("Kimyo", "Kimyo", "Bachelor", 4, None, "O'zbek"),
        ("Fizika", "Fizika", "Bachelor", 4, None, "O'zbek"),
    ],
    "Moscow State University": [
        ("Mexanika va matematika", "Matematika", "Bachelor", 4, 4000, "Russian"),
        ("Fizika", "Fizika", "Bachelor", 4, 4000, "Russian"),
        ("Kimyo", "Kimyo", "Bachelor", 4, 4000, "Russian"),
        ("Huquq", "Huquq", "Bachelor", 4, 5000, "Russian"),
        ("Iqtisodiyot", "Iqtisodiyot", "Bachelor", 4, 5000, "Russian"),
    ],
    "Turin Polytechnic University in Tashkent": [
        ("Muhandislik", "Mexanik muhandislik", "Bachelor", 4, 4500, "English/Italian"),
        ("Muhandislik", "Elektr muhandisligi", "Bachelor", 4, 4500, "English"),
        ("Arxitektura", "Arxitektura va dizayn", "Bachelor", 4, 4500, "English/Italian"),
        ("Kompyuter fanlari", "Kompyuter muhandisligi", "Bachelor", 4, 4500, "English"),
    ],
}

fac_count = 0
for uni_name, fac_list in faculties_data.items():
    try:
        uni = University.objects.get(name__icontains=uni_name[:20])
    except University.DoesNotExist:
        try:
            uni = University.objects.get(name__icontains=uni_name.split()[0])
        except Exception:
            continue
    except Exception:
        continue

    for fac_data in fac_list:
        name, specialty, degree, duration, fee, lang = fac_data
        fac, created = Faculty.objects.get_or_create(
            university=uni, name=specialty,
            defaults={
                'degree': degree,
                'duration_years': duration,
                'tuition_fee_usd': fee,
                'language': lang,
                'is_active': True,
            }
        )
        if created:
            fac_count += 1

    print(f"  ✅ {uni.short_name or uni.name[:30]}: {Faculty.objects.filter(university=uni).count()} ta fakultet")

print(f"\n📊 Jami {fac_count} ta yangi fakultet qo'shildi!")

# ── 5. AI LIMIT OSHIRISH ──────────────────────────────
print("\n🤖 AI limit yangilanmoqda (config/settings/base.py)...")
print("  AI_DAILY_FREE_LIMIT=50 ga o'zgartiring!")
print("  .env faylida yoki settings da o'zgartiring")

print("\n" + "=" * 55)
print("  ✅ HAMMA NARSA TAYYOR!")
print("=" * 55)
print("\nBot qayta ishga tushiring:")
print("  python bot\\main.py")


# ── 5. UNIVERSITY SYNC ────────────────────────────────
print("\n🏫 Universitetlar yangilanmoqda...")
try:
    import subprocess
    result = subprocess.run(
        ['python', 'scripts/sync_universities.py'],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        print("  ✅ Universitetlar muvaffaqiyatli yangilandi!")
    else:
        print("  ⚠️  Sync muammo:", result.stderr[:200])
except Exception as e:
    print(f"  ⚠️  Sync ishga tushmadi: {e}")
    print("  Qo'lda: python scripts/sync_universities.py")
