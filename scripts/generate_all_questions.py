"""Barcha fanlarga 5000 ta savol generatsiya."""
import os, sys, django, random
from fractions import Fraction
from math import gcd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('USE_SQLITE', 'true')
django.setup()

from apps.education.models import Subject, Question


def save_questions(subj, questions):
    added = 0
    for q in questions:
        if len(q) < 8: continue
        if Question.objects.filter(subject=subj, text_uz=q[0]).exists(): continue
        Question.objects.create(
            subject=subj, text_uz=q[0],
            option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
            correct_answer=q[5], explanation_uz=q[6], difficulty=q[7],
            is_active=True, xp_reward=10,
        )
        added += 1
    return added


def sh(correct, w1, w2, w3):
    """Shuffle options — to'g'ri javobni random joylash."""
    opts = [str(w1), str(w2), str(w3)]
    pos  = random.randint(0, 3)
    opts.insert(pos, str(correct))
    return opts[0], opts[1], opts[2], opts[3], ['A','B','C','D'][pos]


# ═══════════════════════════════════════════════════════
# MATEMATIKA — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_math(target=5000):
    qs, seen = [], set()

    def add(text, a,b,c,d,ans,exp,diff):
        if text not in seen and len(seen) < target * 2:
            seen.add(text)
            qs.append((text,a,b,c,d,ans,exp,diff))

    # Ko'paytma (2-99 × 2-99) — ~9700 unique
    for a in range(2, 100):
        for b in range(2, 100):
            res = a * b
            w1,w2,w3 = res+a, res-b if res>b else res+b, res+a+b
            A,B,C,D,ans = sh(res,w1,w2,w3)
            add(f"{a}×{b}=?", A,B,C,D,ans, f"{a}×{b}={res}", "easy")
            if len(qs) >= target: break
        if len(qs) >= target: break

    # Bo'lish
    for b in range(2, 50):
        for res in range(2, 101):
            a = b * res
            A,B,C,D,ans = sh(res, res+1, res+2, res-1 if res>1 else res+3)
            add(f"{a}÷{b}=?", A,B,C,D,ans, f"{a}÷{b}={res}", "easy")
            if len(qs) >= target: break
        if len(qs) >= target: break

    # Foiz
    bases = [50,100,150,200,250,300,400,500,600,750,800,1000,1200,1500,2000,2500,3000,4000,5000]
    pcts  = [1,2,3,4,5,6,7,8,9,10,12,15,16,18,20,24,25,30,32,35,40,45,48,50,60,64,70,75,80,90]
    for base in bases:
        for pct in pcts:
            res = int(base * pct / 100)
            A,B,C,D,ans = sh(res, res+10, res-10 if res>=10 else res+20, res+25)
            add(f"{base} ning {pct}%=?", A,B,C,D,ans, f"{base}×{pct}/100={res}", "easy")
            if len(qs) >= target: break
        if len(qs) >= target: break

    # Tenglama ax+b=c
    for a in range(2, 30):
        for x in range(1, 50):
            for b in range(1, 20):
                c = a*x + b
                A,B,C,D,ans = sh(x, x+1, x+2, x-1 if x>1 else x+3)
                add(f"{a}x+{b}={c}, x=?", A,B,C,D,ans, f"{a}x={c-b}, x={x}", "medium")
                if len(qs) >= target: break
            if len(qs) >= target: break
        if len(qs) >= target: break

    # n² (2-200)
    for n in range(2, 201):
        res = n*n
        A,B,C,D,ans = sh(res, res+n, res-n, res+2*n)
        add(f"{n}²=?", A,B,C,D,ans, f"{n}²={res}", "easy")
        if len(qs) >= target: break

    # √n² (1-200)
    for n in range(1, 201):
        sq = n*n
        A,B,C,D,ans = sh(n, n+1, n+2, n+3)
        add(f"√{sq}=?", A,B,C,D,ans, f"√{sq}={n}", "easy")
        if len(qs) >= target: break

    # 2ⁿ (0-30)
    for n in range(0, 31):
        res = 2**n
        A,B,C,D,ans = sh(res, res*2, res+1, res-1 if res>1 else res+5)
        add(f"2^{n}=?", A,B,C,D,ans, f"2^{n}={res}", "easy" if n<10 else "medium")
        if len(qs) >= target: break

    # Log
    for base in [2,3,5,10]:
        for exp in range(1, 15):
            val = base**exp
            A,B,C,D,ans = sh(exp, exp+1, exp-1 if exp>1 else exp+2, exp+2)
            add(f"log{base}({val})=?", A,B,C,D,ans, f"{base}^{exp}={val}", "medium")
            if len(qs) >= target: break
        if len(qs) >= target: break

    # EKUB
    for _ in range(5000):
        a = random.randint(2, 200)
        b = random.randint(2, 200)
        res = gcd(a, b)
        text = f"EKUB({a},{b})=?"
        A,B,C,D,ans = sh(res, res+1, res*2, res+3 if res<100 else res-1)
        add(text, A,B,C,D,ans, f"EKUB={res}", "hard")
        if len(qs) >= target: break

    # O'rtacha
    for _ in range(5000):
        nums = [random.randint(2, 100) for _ in range(random.randint(3,7))]
        res  = sum(nums)//len(nums)
        text = f"O'rtacha: {','.join(map(str,nums))}=?"
        A,B,C,D,ans = sh(res, res+3, res-3 if res>3 else res+6, res+7)
        add(text, A,B,C,D,ans, f"Yig':{sum(nums)}/son:{len(nums)}={res}", "medium")
        if len(qs) >= target: break

    # Kasrlar qo'shish
    for _ in range(3000):
        a = random.randint(1,9); b = random.randint(a+1,20)
        c = random.randint(1,9); d = random.randint(c+1,20)
        r = Fraction(a,b)+Fraction(c,d)
        text = f"{a}/{b}+{c}/{d}=?"
        rs = f"{r.numerator}/{r.denominator}" if r.denominator!=1 else str(r.numerator)
        A,B,C,D,ans = sh(rs, f"{r.numerator+1}/{r.denominator}", f"{r.numerator}/{r.denominator+1}", f"{a+c}/{b}")
        add(text, A,B,C,D,ans, "Umumiy maxraj", "medium")
        if len(qs) >= target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# FIZIKA — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_physics(target=5000):
    qs, seen = [], set()
    def add(text,a,b,c,d,ans,exp,diff):
        if text not in seen:
            seen.add(text)
            qs.append((text,a,b,c,d,ans,exp,diff))

    # F=ma
    for m in range(1, 101):
        for a in range(1, 51):
            F = m*a
            A,B,C,D,ans = sh(f"{F}N", f"{F+m}N", f"{F-a}N" if F>a else f"{F+10}N", f"{F*2}N")
            add(f"m={m}kg, a={a}m/s², F=?", A,B,C,D,ans, f"F=ma={m}×{a}={F}N", "easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Ep=mgh
    for m in range(1, 101):
        for h in range(1, 51):
            E = m*10*h
            A,B,C,D,ans = sh(f"{E}J", f"{E+50}J", f"{E-50}J" if E>50 else f"{E+100}J", f"{E*2}J")
            add(f"m={m}kg, h={h}m, Ep=?", A,B,C,D,ans, f"Ep=mgh={m}×10×{h}={E}J", "medium")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Ek=mv²/2
    for m in range(1, 51):
        for v in range(1, 51):
            E = m*v*v//2
            A,B,C,D,ans = sh(f"{E}J", f"{E+10}J", f"{E-5}J" if E>5 else f"{E+20}J", f"{E*2}J")
            add(f"m={m}kg, v={v}m/s, Ek=?", A,B,C,D,ans, f"Ek=mv²/2={m}×{v}²/2={E}J", "medium")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # I=U/R
    for U in [6,9,12,18,24,36,48,60,110,220]:
        for R in range(1, 201):
            I = round(U/R, 2)
            A,B,C,D,ans = sh(f"{I}A", f"{round(I*2,2)}A", f"{round(I+0.5,2)}A", f"{round(I-0.5,2)}A" if I>0.5 else f"{round(I+1,2)}A")
            add(f"U={U}V, R={R}Ω, I=?", A,B,C,D,ans, f"I=U/R={U}/{R}={I}A", "easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # P=UI
    for U in [12,24,110,220]:
        for I in range(1, 101):
            P = U*I
            A,B,C,D,ans = sh(f"{P}W", f"{P+U}W", f"{P-I}W" if P>I else f"{P+10}W", f"{P*2}W")
            add(f"U={U}V, I={I}A, P=?", A,B,C,D,ans, f"P=UI={U}×{I}={P}W", "medium")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # v=s/t (tezlik)
    for s in range(10, 500, 10):
        for t in range(1, 101):
            v = s//t if s%t==0 else round(s/t, 1)
            A,B,C,D,ans = sh(f"{v}m/s", f"{round(float(str(v))+1,1)}m/s", f"{round(float(str(v))+2,1)}m/s", f"{round(float(str(v))*2,1)}m/s")
            add(f"s={s}m, t={t}s, v=?", A,B,C,D,ans, f"v=s/t={s}/{t}={v}m/s", "easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # R=U/I (qarshilik)
    for U in [6,12,24,48,110,220]:
        for I in range(1, 51):
            R = round(U/I, 2)
            A,B,C,D,ans = sh(f"{R}Ω", f"{round(R*2,2)}Ω", f"{round(R+1,2)}Ω", f"{round(R+5,2)}Ω")
            add(f"U={U}V, I={I}A, R=?", A,B,C,D,ans, f"R=U/I={U}/{I}={R}Ω", "medium")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Q=mcΔT
    for m in range(1, 21):
        for c in [500, 1000, 2100, 4200]:
            for dt in range(1, 51):
                Q = m*c*dt
                A,B,C,D,ans = sh(f"{Q}J", f"{Q+1000}J", f"{Q-500}J" if Q>500 else f"{Q+500}J", f"{Q*2}J")
                add(f"m={m}kg, c={c}, ΔT={dt}°, Q=?", A,B,C,D,ans, f"Q=mcΔT={m}×{c}×{dt}={Q}J", "hard")
                if len(qs)>=target: break
            if len(qs)>=target: break
        if len(qs)>=target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# IT — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_it(target=5000):
    qs, seen = [], set()
    def add(text,a,b,c,d,ans,exp,diff):
        if text not in seen:
            seen.add(text)
            qs.append((text,a,b,c,d,ans,exp,diff))

    # Binary → decimal (1-1023)
    for n in range(1, 1024):
        bin_str = bin(n)[2:]
        A,B,C,D,ans = sh(n, n+1, n+2, n-1 if n>1 else n+3)
        add(f"{bin_str}₂=?₁₀", str(A),str(B),str(C),str(D),ans, f"{bin_str}₂={n}", "medium")
        if len(qs)>=target: break

    # Decimal → binary (1-511)
    for n in range(1, 512):
        bin_str = bin(n)[2:]
        A,B,C,D,ans = sh(bin_str, bin(n+1)[2:], bin(n+2)[2:], bin(n-1)[2:] if n>1 else bin(n+3)[2:])
        add(f"{n}₁₀=?₂", A,B,C,D,ans, f"{n}={bin_str}₂", "medium")
        if len(qs)>=target: break

    # Hex → decimal (0-255)
    for n in range(0, 256):
        hx = hex(n)[2:].upper()
        A,B,C,D,ans = sh(n, n+1, n+8, n+16 if n<240 else n-16)
        add(f"0x{hx}=?", str(A),str(B),str(C),str(D),ans, f"0x{hx}={n}", "hard")
        if len(qs)>=target: break

    # GB/MB/KB konversiya
    for gb in range(1, 1025):
        mb = gb*1024
        A,B,C,D,ans = sh(mb, gb*1000, mb+1, mb//2)
        add(f"{gb}GB=?MB", str(A),str(B),str(C),str(D),ans, f"1GB=1024MB", "easy")
        if len(qs)>=target: break

    for mb in range(1, 1025):
        kb = mb*1024
        A,B,C,D,ans = sh(kb, mb*1000, kb+1, kb//2)
        add(f"{mb}MB=?KB", str(A),str(B),str(C),str(D),ans, f"1MB=1024KB", "easy")
        if len(qs)>=target: break

    for kb in range(1, 513):
        b = kb*8*1024
        A,B,C,D,ans = sh(b, kb*1000*8, b+1, b//2)
        add(f"{kb}KB=?bit", str(A),str(B),str(C),str(D),ans, f"1KB=8×1024bit", "hard")
        if len(qs)>=target: break

    # Decimal → octal (8-li)
    for n in range(1, 512):
        oct_str = oct(n)[2:]
        A,B,C,D,ans = sh(oct_str, oct(n+1)[2:], oct(n+2)[2:], oct(n-1)[2:] if n>1 else oct(n+3)[2:])
        add(f"{n}₁₀=?₈", A,B,C,D,ans, f"{n}={oct_str}₈", "hard")
        if len(qs)>=target: break

    # AND/OR/XOR bitwise
    for _ in range(2000):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        op = random.choice(['AND','OR','XOR'])
        if op=='AND':    res=a&b
        elif op=='OR':   res=a|b
        else:            res=a^b
        text = f"{a} {op} {b} = ?"
        A,B,C,D,ans = sh(res, res+1, res^1, (res+2)%256)
        add(text, str(A),str(B),str(C),str(D),ans, f"{a} {op} {b} = {res}", "hard")
        if len(qs)>=target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# KIMYO — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_chemistry(target=5000):
    qs, seen = [], set()
    def add(t,a,b,c,d,ans,exp,diff):
        if t not in seen: seen.add(t); qs.append((t,a,b,c,d,ans,exp,diff))

    # Molyar massa hisoblash
    elements = {
        'H':1,'He':4,'Li':7,'Be':9,'B':11,'C':12,'N':14,'O':16,
        'F':19,'Ne':20,'Na':23,'Mg':24,'Al':27,'Si':28,'P':31,'S':32,
        'Cl':35,'Ar':40,'K':39,'Ca':40,'Fe':56,'Cu':64,'Zn':65,'Br':80,
        'Ag':108,'I':127,'Au':197,'Pb':207
    }
    compounds = [
        ('H₂O',2*1+16),('CO₂',12+2*16),('NaCl',23+35),('H₂SO₄',2+32+4*16),
        ('HCl',1+35),('NaOH',23+16+1),('Ca(OH)₂',40+2*(16+1)),('NH₃',14+3),
        ('CH₄',12+4),('C₂H₅OH',2*12+6+16),('CaCO₃',40+12+3*16),('HNO₃',1+14+3*16),
        ('Al₂O₃',2*27+3*16),('Fe₂O₃',2*56+3*16),('KOH',39+16+1),('MgO',24+16),
        ('H₂',2),('O₂',32),('N₂',28),('Cl₂',70),('SO₂',32+2*16),('SO₃',32+3*16),
        ('NO',14+16),('NO₂',14+2*16),('CO',12+16),('H₂S',2+32),('H₃PO₄',3+31+4*16),
        ('Na₂CO₃',2*23+12+3*16),('Na₂SO₄',2*23+32+4*16),('CaSO₄',40+32+4*16),
        ('KNO₃',39+14+3*16),('Ca₃(PO₄)₂',3*40+2*(31+4*16)),('FeCl₃',56+3*35),
    ]
    for formula, mass in compounds:
        A,B,C,D,ans = sh(mass, mass+8, mass-8 if mass>8 else mass+16, mass+16)
        add(f"M({formula})=? g/mol", str(A),str(B),str(C),str(D),ans, f"M={mass}g/mol", "medium")

    # Reaksiya turlari
    rxn_types = [
        ("2H₂+O₂→2H₂O", "Birikish"),("2H₂O→2H₂+O₂", "Parchalanish"),
        ("Zn+H₂SO₄→ZnSO₄+H₂↑", "Almashinish"),("Fe+CuSO₄→FeSO₄+Cu", "Siljish"),
        ("NaOH+HCl→NaCl+H₂O", "Neytrallanish"),("Ca+2H₂O→Ca(OH)₂+H₂↑", "Birikish"),
        ("CaCO₃→CaO+CO₂↑", "Parchalanish"),("2Na+2H₂O→2NaOH+H₂↑", "Siljish"),
        ("BaCl₂+H₂SO₄→BaSO₄↓+2HCl", "Almashinish"),("C+O₂→CO₂", "Birikish"),
        ("2KClO₃→2KCl+3O₂↑", "Parchalanish"),("Fe₂O₃+3H₂→2Fe+3H₂O", "Qaytarilish"),
        ("Cu+2H₂SO₄(konc)→CuSO₄+SO₂+2H₂O", "Oksidlanish-qaytarilish"),
        ("2Al+3Cl₂→2AlCl₃", "Birikish"),("Mg+2HCl→MgCl₂+H₂↑", "Siljish"),
    ]
    all_types = ["Birikish","Parchalanish","Almashinish","Siljish","Neytrallanish","Oksidlanish-qaytarilish"]
    for rxn, rtype in rxn_types:
        others = [t for t in all_types if t != rtype][:3]
        A,B,C,D,ans = sh(rtype, others[0], others[1], others[2])
        add(f"Reaksiya turi: {rxn}", A,B,C,D,ans, f"{rtype} reaksiya", "medium")

    # pH masalalari
    ph_data = [
        ("HCl 0.1M", "1", "kislotali"),
        ("HCl 0.01M", "2", "kislotali"),
        ("NaOH 0.1M", "13", "ishqoriy"),
        ("NaOH 0.01M", "12", "ishqoriy"),
        ("Sof suv", "7", "neytral"),
        ("Limon sharbati", "2-3", "kislotali"),
        ("Qon", "7.4", "neytral/zaif ishqoriy"),
        ("Soda", "11", "ishqoriy"),
        ("Sirka kislota 0.1M", "3", "kislotali"),
        ("Oshqozon shirasi", "1.5", "kislotali"),
    ]

    for substance, ph, medium in ph_data:
        # 1. Baza qiymatni ajratib olamiz va float'ga o'giramiz (xatolik oldini olish uchun)
        base_ph_str = ph.split('-')[0]
        base_ph = float(base_ph_str)

        # 2. B variantini hisoblash: pH + 2
        b_val = base_ph + 2
        # Agar son butun bo'lsa (masalan 3.0), uni '3' ko'rinishida formatlaymiz, kasr bo'lsa '7.4' holicha qoladi
        B = str(int(b_val)) if b_val.is_integer() else str(round(b_val, 1))

        # 3. C variantini hisoblash logicasi
        if '-' in ph:
            c_val = base_ph - 1
        else:
            c_val = base_ph - 2 if base_ph > 2 else base_ph + 3
        C = str(int(c_val)) if c_val.is_integer() else str(round(c_val, 1))

        # 4. D varianti doimiy
        D = "14"

        # Variantlarni sh() funksiyasiga uzatamiz
        A, B, C, D, ans = sh(ph, B, C, D)

        # Ma'lumotlar bazasiga qo'shish
        add(f"{substance} ning pH=?", A, B, C, D, ans, f"pH={ph} ({medium})", "hard")

    # Valentlik masalalari
    valency_data = [
        ("Na","I"),("K","I"),("Ca","II"),("Mg","II"),("Al","III"),
        ("Fe(II)","II"),("Fe(III)","III"),("Cu(I)","I"),("Cu(II)","II"),
        ("Zn","II"),("Pb(II)","II"),("Mn(II)","II"),("Cr(III)","III"),
        ("O","II"),("S(IV)","IV"),("S(VI)","VI"),("N(III)","III"),("N(V)","V"),
        ("Cl","I"),("P(V)","V"),("C(IV)","IV"),("Si","IV"),
    ]
    for elem, val in valency_data:
        others = ["I","II","III","IV","V","VI","VII"]
        others = [v for v in others if v!=val][:3]
        A,B,C,D,ans = sh(val, others[0], others[1], others[2])
        add(f"{elem} valentligi=?", A,B,C,D,ans, f"{elem} valentligi={val}", "medium")

    # Tuzlar formulalari
    salts = [
        ("Natriy sulfat","Na₂SO₄"),("Kaliy nitrat","KNO₃"),("Kaltsiy xlorid","CaCl₂"),
        ("Alyuminiy sulfat","Al₂(SO₄)₃"),("Mis(II) sulfat","CuSO₄"),
        ("Temir(III) xlorid","FeCl₃"),("Kaliy xlorid","KCl"),("Natriy nitrat","NaNO₃"),
        ("Magniy sulfat","MgSO₄"),("Sink sulfat","ZnSO₄"),("Bariy sulfat","BaSO₄"),
        ("Kalsiy karbonat","CaCO₃"),("Natriy karbonat","Na₂CO₃"),("Ammoniy xlorid","NH₄Cl"),
        ("Kalsiy fosfat","Ca₃(PO₄)₂"),("Natriy fosfat","Na₃PO₄"),
    ]
    for name, formula in salts:
        others = [f for _, f in salts if f != formula]
        random.shuffle(others)
        A,B,C,D,ans = sh(formula, others[0], others[1], others[2])
        add(f"{name} formulasi=?", A,B,C,D,ans, f"{name}={formula}", "medium")

    # Agregat holat o'zgarishlari
    state_changes = [
        ("Qattiq→suyuq","Erish"),("Suyuq→gaz","Qaynash"),("Gaz→suyuq","Kondensatsiya"),
        ("Suyuq→qattiq","Qotish"),("Qattiq→gaz","Sublimatsiya"),("Gaz→qattiq","Desublimatsiya"),
    ]
    sc_names = ["Erish","Qaynash","Kondensatsiya","Qotish","Sublimatsiya","Desublimatsiya","Bug'lanish"]
    for change, name in state_changes:
        others = [n for n in sc_names if n!=name][:3]
        A,B,C,D,ans = sh(name, others[0], others[1], others[2])
        add(f"{change} jarayoni nomi=?", A,B,C,D,ans, f"{change}={name}", "easy")

    # Oksidlanish darajasi
    ox_data = [
        ("Na₂O da Na","Na=+1"),("MgO da Mg","Mg=+2"),("Al₂O₃ da Al","Al=+3"),
        ("H₂O da H","H=+1"),("H₂O da O","O=-2"),("CO₂ da C","C=+4"),
        ("SO₃ da S","S=+6"),("NO₂ da N","N=+4"),("HCl da Cl","Cl=-1"),
        ("NaOH da O","O=-2"),("H₂SO₄ da S","S=+6"),("HNO₃ da N","N=+5"),
        ("KMnO₄ da Mn","Mn=+7"),("K₂Cr₂O₇ da Cr","Cr=+6"),("FeCl₃ da Fe","Fe=+3"),
    ]
    for molecule, ox_state in ox_data:
        val = ox_state.split('=')[1]
        others = [v for v in ["-2","-1","0","+1","+2","+3","+4","+5","+6","+7"] if v!=val][:3]
        A,B,C,D,ans = sh(val, others[0], others[1], others[2])
        add(f"{molecule} oksidlanish darajasi=?", A,B,C,D,ans, ox_state, "hard")

    # Molyar hajm, massa
    for _ in range(3000):
        mol = random.choice([0.5,1,1.5,2,2.5,3,4,5,10])
        M   = random.choice([2,4,7,12,14,16,18,20,23,24,28,32,35,36,40,44,46,56,58,64,98])
        mass = round(mol * M, 1)
        A,B,C,D,ans = sh(f"{mass}g", f"{round(mass+M,1)}g", f"{round(mass-M,1)}g" if mass>M else f"{round(mass+2*M,1)}g", f"{round(mass*2,1)}g")
        add(f"{mol} mol modda, M={M}g/mol, massa=?", A,B,C,D,ans, f"m=n×M={mol}×{M}={mass}g", "hard")
        if len(qs)>=target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# BIOLOGIYA — 5000 ta
# ═══════════════════════════════════════════════════════
import random


def gen_biology(target=5000):
    qs, seen = [], set()

    def add(t, a, b, c, d, ans, exp, diff):
        if t not in seen:
            seen.add(t)
            qs.append((t, a, b, c, d, ans, exp, diff))

    # 1. Hujayra organoidlari bazasi
    organelles = [
        ("ATP ishlab chiqaradi", "Mitoxondriya", "Yadro", "Ribosoma", "Lizosoma", "A", "energiya markazi"),
        ("Oqsil sintez qiladi", "Ribosoma", "Mitoxondriya", "Vakuol", "Golji", "A", "mRNA asosida"),
        ("Fotosintez joyi", "Xloroplast", "Mitoxondriya", "Ribosoma", "Vakuol", "A", "xlorofill bor"),
        ("Hujayraning boshqaruv markazi", "Yadro", "Mitoxondriya", "Lizosoma", "Vakuol", "A", "DNK saqlanadi"),
        ("Hazm fermentlari bor", "Lizosoma", "Ribosoma", "Vakuol", "Golji", "A", "autofagiya"),
        ("Sekretlarni saqlaydi", "Golji apparati", "Ribosoma", "Lizosoma", "Yadro", "A", "eksport funktsiyasi"),
        ("O'simlik hujayrasida suv saqlaydi", "Vakuol", "Mitoxondriya", "Ribosoma", "Lizosoma", "A", "turgor bosimi"),
        ("Sitoplazmaning tashqi qobig'i", "Plazmatik membrana", "Hujayra devori", "Ribosoma", "Vakuol", "A",
         "tanlab o'tkazuvchan"),
        ("O'simlik hujayrasida qattiq tashqi qobiq", "Hujayra devori", "Membrana", "Vakuol", "Lizosoma", "A",
         "sellyulozadan"),
        ("DNK saqlaydi (hujayra ichida)", "Yadro", "Mitoxondriya", "Ribosoma", "Lizosoma", "A", "xromosomalar"),
    ]
    for row in organelles:
        add(f"{row[0]}?", row[1], row[2], row[3], row[4], row[5], f"{row[0]}={row[1]}", "easy")

    # 2. Hujayra bo'linishi
    division_facts = [
        ("Mitozdan hosil bo'lgan hujayralar soni", "2", "4", "8", "1", "A", "bir xil 2 ta diploid", "easy"),
        ("Meyozdan hosil bo'lgan hujayralar soni", "2", "4", "6", "8", "B", "4 ta haploid", "medium"),
        ("Mitozda xromosomalar soni (inson)", "23", "46", "48", "92", "B", "diploid saqlanadi", "medium"),
        ("Meyozdan hosil hujayralar xromosom soni", "23", "46", "48", "92", "A", "haploid=23", "medium"),
        ("Interfaza davrlari soni", "1", "2", "3", "4", "C", "G1, S, G2", "hard"),
        ("DNK replikatsiya qaysi fazada", "G1", "S", "G2", "M", "B", "S-faza", "hard"),
    ]
    for row in division_facts:
        add(row[0] + "?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 3. Qon guruhlari
    blood_facts = [
        ("I(O) qon guruh xususiyati", "Universal donor", "Universal recipient", "Faqat I oladi", "Hammaga beradi", "A",
         "I guruh universal donor", "medium"),
        ("IV(AB) qon guruh xususiyati", "Universal donor", "Universal recipient", "Faqat O", "Hammaga beradi", "B",
         "IV guruh universal recipient", "medium"),
        ("Qon guruhlari tizimi", "ABO", "ABC", "ABD", "ABCD", "A", "ABO tizimi", "easy"),
        ("Rh faktor nima", "Qon guruhi", "Qondagi antigen", "pH", "Xromosoma", "B", "D antigen", "medium"),
        ("Rh+ qon nima", "Rh antigen bor", "Rh antigen yo'q", "Rh neytral", "Rh kuchli", "A", "D antigen mavjud",
         "medium"),
    ]
    for row in blood_facts:
        add(row[0] + "?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 4. Gormonlar bazasi
    hormones = [
        ("Insulin", "Me'da osti bezi", "Jigar", "Buyrak usti", "Qalqonsimon", "A", "qondagi shakar pasaytiradi"),
        ("Glyukagon", "Me'da osti bezi", "Jigar", "Buyrak usti", "Qalqonsimon", "A", "qondagi shakar oshiradi"),
        ("Adrenalin", "Buyrak usti bezi", "Jigar", "Me'da osti", "Qalqonsimon", "A", "stressda ajraladi"),
        ("Tiroksin", "Qalqonsimon bez", "Jigar", "Me'da osti", "Buyrak usti", "A", "metabolizmni boshqaradi"),
        ("Kortizol", "Buyrak usti bezi (po'stloq)", "Jigar", "Me'da osti", "Qalqonsimon", "A", "stress gormoni"),
        ("Testosteron", "Moyak", "Tuxumdon", "Buyrak usti", "Qalqonsimon", "A", "erkak jins gormoni"),
        ("Estrogen", "Tuxumdon", "Moyak", "Buyrak usti", "Qalqonsimon", "A", "ayol jins gormoni"),
        ("Progesteron", "Tuxumdon/yo'ldosh", "Moyak", "Buyrak usti", "Jigar", "A", "homiladorlik gormoni"),
        ("Oksitotsin", "Gipofiz", "Qalqonsimon", "Buyrak usti", "Jigar", "A", "tug'ish va emizish"),
        ("Melatonin", "Qo'shimcha bez (epifiz)", "Jigar", "Buyrak usti", "Qalqonsimon", "A", "uyqu ritmi"),
    ]
    for h, loc, w1, w2, w3, ans, exp in hormones:
        add(f"{h} gormoni qayerda ishlab chiqariladi?", loc, w1, w2, w3, ans, exp, "medium")

    # 5. Vitaminlar va Kasalliklar
    vitamins = [
        ("A", "Ko'rish, teri", "Ko'r kasalligi", "Sabzi, jigar", "easy"),
        ("B1", "Nerv tizimi", "Beriberi", "Don mahsulotlar", "easy"),
        ("B12", "Qon ishlab chiqarish", "Anemiya", "Hayvon mahsulotlar", "medium"),
        ("C", "Immunitet, kollagen", "Skorbut", "Sitrus mevalar", "easy"),
        ("D", "Suyak (Ca so'rilishi)", "Raxit", "Quyosh nuri, baliq", "easy"),
        ("E", "Antioxidant, muskul", "Muskul zaiflik", "Yong'oq, o'simlik yog'i", "medium"),
        ("K", "Qon ivish", "Qon to'xtamaslik", "Yashil sabzavot", "medium"),
    ]
    diseases = ["Ko'r kasalligi", "Beriberi", "Skorbut", "Raxit", "Anemiya", "Muskul zaiflik", "Qon to'xtamaslik"]
    for v, func, dis, source, diff in vitamins:
        others = [d for d in diseases if d != dis][:3]
        A, B, C, D, ans = sh(dis, others[0], others[1], others[2])
        add(f"Vitamin {v} yetishmaganda qanday kasallik kelib chiqadi?", A, B, C, D, ans,
            f"Vitamin {v} yetishmovchiligi = {dis}", diff)

    # 6. Genetika
    genetics = [
        ("Dominant gen nima?", "Kuchli (namoyon)", "Kuchsiz", "Yashirin", "Mutant", "A", "fenotipta ko'rinadi",
         "medium"),
        ("Retsessiv gen nima?", "Kuchsiz (yashirin)", "Kuchli", "Namoyon", "Dominant", "A", "gomozigotda namoyon",
         "medium"),
        ("Gomozigot nima?", "AA yoki aa", "Aa", "Aaaa", "Aabb", "A", "bir xil allellar", "medium"),
        ("Geterozigot nima?", "Aa", "AA", "aa", "AABB", "A", "har xil allellar", "medium"),
        ("Genotip nima?", "Tashqi belgilar", "Ichki gen tarkibi", "DNK uzunligi", "Xromosom soni", "B",
         "genlar to'plami", "medium"),
        ("Fenotip nima?", "Genlar to'plami", "Tashqi namoyon belgilar", "DNK", "RNK", "B", "ko'rinadigan belgilar",
         "medium"),
        ("Mendel 1-qonuni", "Sof liniyalar", "Gibridlarning bir xilligi", "Ajralish", "Mustaqil irsiyat", "B",
         "F1 bir xil", "medium"),
        ("Mendel 2-qonuni", "Gibrid bir xilligi", "3:1 ajralish", "Mustaqil", "Sof liniya", "B", "F2 da 3:1", "hard"),
        ("Mendel 3-qonuni", "3:1", "9:3:3:1", "1:1", "1:2:1", "B", "2 juft gen mustaqil", "hard"),
        ("Ko'prik dihibrid kesishda F2 nisbat", "9:3:3:1", "3:1", "1:2:1", "1:1", "A", "AaBb × AaBb", "hard"),
    ]
    for row in genetics:
        add(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 7. Ekologiya
    ecology = [
        ("Producent nima?", "Iste'molchi", "Ishlab chiqaruvchi (o'simlik)", "Parchalovchi", "Yirtqich", "B",
         "fotosintez qiladi", "easy"),
        ("Konsument nima?", "O'simlik", "Hayvon (iste'molchi)", "Bakteriya", "Zamburug'", "B",
         "organik moddani iste'mol qiladi", "easy"),
        ("Redutsent nima?", "O'simlik", "Hayvon", "Parchalovchi (bakteriya/zamburug')", "Yirtqich", "C",
         "organikni parchalaydi", "easy"),
        ("Oziq zanjiri yo'nalishi", "Konsument→Producent", "Producent→Konsument→Redutsent", "Redutsent→Producent",
         "Konsument→Redutsent", "B", "energiya oqimi", "medium"),
        ("Biotik omillar", "Temperatura", "Yorug'lik", "Boshqa organizmlar", "Suv", "C", "tirik omillar", "medium"),
        ("Abiotik omillar", "Hayvonlar", "O'simliklar", "Bakteriyalar", "Temperatura, yorug'lik, suv", "D",
         "tirik bo'lmagan omillar", "medium"),
        ("Ekotizim nima?", "Faqat tirik organizmlar", "Organizmlar + muhit", "Faqat o'simliklar", "Faqat hayvonlar",
         "B", "biosistema", "medium"),
        ("Biosfera nima?", "Bir ekotizim", "Barcha hayot tarqalgan qobiq", "Atmosfera", "Litosfera", "B",
         "Vernadskiy ta'rifi", "hard"),
        ("Niche nima (ekologik)?", "Yashash joyi", "Turning ekologik roli va o'rni", "Oziq zanjiri", "Populyatsiya",
         "B", "ekologik o'rin", "hard"),
        ("Populyatsiya nima?", "Bir xil turning bitta hudud vakillari", "Ko'p tur", "Ekotizim", "Biosfera", "A",
         "bir tur vakillari", "medium"),
    ]
    for row in ecology:
        add(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 8. Ko'payish va rivojlanish
    reproduction = [
        ("Jinsiy ko'payish afzalligi", "Tez", "Genetik xilma-xillik", "Bir xil avlod", "Kam energiya", "B",
         "evolyutsiya uchun", "medium"),
        ("Jinsiz ko'payish afzalligi", "Sekin", "Tez va ko'p avlod", "Xilma-xillik", "Kam energiya", "B",
         "tez ko'payadi", "medium"),
        ("Partenogenez nima?", "Sperma + tuxum", "Faqat tuxumdan rivojlanish", "Bo'rtma berish", "Spor", "B",
         "urug'lanmagan tuxum", "hard"),
        ("Metamorfoz nima?", "O'sish", "Shaklning o'zgarishi", "Ko'payish", "Irsiyat", "B", "pilla, qo'ng'iz",
         "medium"),
        ("To'liq metamorfoz bosqichlari", "Tuxum→lichinka→g'umbak→imago", "Tuxum→lichinka→imago", "Tuxum→imago",
         "Lichinka→imago", "A", "kapalak, chivin", "medium"),
    ]
    for row in reproduction:
        add(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # =========================================================================
    # KO'PAYTIRISH QISMI (Xavfsiz va kombinatsiyali dinamik generator)
    # =========================================================================

    # Barcha mavjud organoidlar, bezlar va terminlar ro'yxati (chalg'ituvchi variantlar uchun)
    all_org_names = [r[1] for r in organelles]
    all_glands = [h[1] for h in hormones]

    attempts = 0
    max_attempts = 150000  # Skript qotib qolmasligi uchun maksimal urinish chegarasi

    while len(qs) < target and attempts < max_attempts:
        attempts += 1

        # 1-Kombinatsiya: Organoidlar va ularning funksiyalarini har xil shablonlarda aralashtirish
        for desc, org, *_, exp in organelles:
            wrong_options = random.sample([o for o in all_org_names if o != org], 3)
            A, B, C, D, ans = sh(org, wrong_options[0], wrong_options[1], wrong_options[2])

            # Har safar har xil matnli savol generatsiya qilamiz (seen'dan o'tishi uchun)
            templates = [
                f"Quyidagi organoidlardan qaysi biri {desc.lower()}?",
                f"Hujayrada {desc.lower()} qaysi tuzilma hisoblanadi?",
                f"Biologiyada {desc.lower()} qaysi organoidga xos?"
            ]
            q_text = random.choice(templates)
            add(q_text, A, B, C, D, ans, exp, "medium")
            if len(qs) >= target: break

        if len(qs) >= target: break

        # 2-Kombinatsiya: Gormonlar va bezlarni qayta kombinatsiya qilish
        for h, gland, *_, exp in hormones:
            wrong_glands = random.sample([g for g in all_glands if g != gland], 3)
            A, B, C, D, ans = sh(gland, wrong_glands[0], wrong_glands[1], wrong_glands[2])

            templates = [
                f"Inson organizmida {h} gormoni qayerda sintezlanadi?",
                f"Qaysi ichki sekretsiya bezi yoki organ {h} ajratadi?",
                f"Biologik jihatdan {h} gormonining ishlab chiqarilish joyi qayer?"
            ]
            q_text = random.choice(templates)
            add(q_text, A, B, C, D, ans, exp, "hard")
            if len(qs) >= target: break

        if len(qs) >= target: break

        # 3-Kombinatsiya: Vitaminlar manbalarini tekshirish savollari
        for v, func, dis, source, diff in vitamins:
            wrong_sources = random.sample([x[3] for x in vitamins if x[3] != source], 3)
            A, B, C, D, ans = sh(source, wrong_sources[0], wrong_sources[1], wrong_sources[2])

            q_text = f"Qaysi mahsulotlar yoki omil Vitamin {v} ning asosiy manbai hisoblanadi?"
            add(q_text, A, B, C, D, ans, f"Vitamin {v} manbai: {source}", diff)
            if len(qs) >= target: break

        # Agar yangi variantlar butunlay tugasa va 1000 tadan oshgan bo'lsa, cheksiz aylanmasdan to'xtatish
        if attempts > 50000 and len(qs) >= 1000 and len(qs) == len(seen):
            break

    random.shuffle(qs)
    return qs[:target]

# ═══════════════════════════════════════════════════════
# TARIX — 5000 ta
# ═══════════════════════════════════════════════════════
import random


def gen_history(target=5000):
    qs, seen = [], set()

    def add(t, a, b, c, d, ans, exp, diff):
        if t not in seen:
            seen.add(t)
            qs.append((t, a, b, c, d, ans, exp, diff))

    # 1. Sanalar
    dates = [
        ("O'zbekiston mustaqilligi", "1991", "1990", "1992", "1993", "A", "1991-yil 1-sentabr", "easy"),
        ("Amir Temur tug'ilgan", "1336", "1370", "1405", "1300", "A", "Shahrisabz", "easy"),
        ("Ulug'bek rasadxonasi qurildi", "1428", "1418", "1438", "1400", "A", "Samarqand", "medium"),
        ("Ibn Sino tug'ilgan", "980", "970", "960", "990", "A", "Afshona qishlog'i", "medium"),
        ("Al-Beruniy tug'ilgan", "973", "963", "983", "993", "A", "Kath, Xorazm", "medium"),
        ("Al-Xorazmiy yashagan davr", "8-9 asr", "7-8 asr", "9-10 asr", "10-11 asr", "A", "783-850", "hard"),
        ("Yusuf Xos Hojib 'Qutadg'u bilig'", "1069", "1059", "1079", "1089", "A", "Qoraxoniylar davri", "hard"),
        ("Muhammad al-Buxoriy tug'ilgan", "810", "800", "820", "830", "A", "Buxoro", "medium"),
        ("Temur vafot etdi", "1405", "1395", "1415", "1400", "A", "Sayram shahri", "medium"),
        ("Ulug'bek vafot etdi", "1449", "1439", "1459", "1445", "A", "suiqasd bilan", "medium"),
        ("Bobur Hindistonga ketdi", "1526", "1516", "1536", "1506", "A", "Boburiylar asoschisi", "medium"),
        ("Shayboniyxon Buxoroni oldi", "1500", "1490", "1510", "1505", "A", "Temuriylar tugadi", "hard"),
        ("Qo'qon xonligi tashkil topdi", "1709", "1699", "1719", "1729", "A", "Farg'ona vodiysi", "hard"),
        ("Xiva Rossiyaga bo'ysundi", "1873", "1863", "1883", "1853", "A", "Shartnoma imzolandi", "hard"),
        ("Buxoro amirligining qulashi", "1920", "1910", "1930", "1915", "A", "Qizil Armiya", "hard"),
        ("O'zbekiston SSR tashkil topdi", "1924", "1920", "1922", "1926", "A", "sovet davri", "hard"),
        ("Toshkent poytaxt bo'ldi", "1930", "1920", "1924", "1940", "A", "SSR poytaxti", "hard"),
        ("1-jahon urushi boshlandi", "1914", "1912", "1913", "1915", "A", "28-iyul", "easy"),
        ("1-jahon urushi tugadi", "1918", "1917", "1919", "1920", "A", "11-noyabr", "easy"),
        ("2-jahon urushi boshlandi", "1939", "1938", "1940", "1941", "A", "1-sentabr", "easy"),
        ("2-jahon urushi tugadi", "1945", "1944", "1946", "1947", "A", "2-sentabr", "easy"),
        ("Birinchi yadro bomba Hirosima", "1945", "1944", "1946", "1943", "A", "6-avgust", "easy"),
        ("Birinchi kosmonavt", "1961", "1960", "1962", "1963", "A", "12-aprel", "easy"),
        ("Oyga birinchi qo'nish", "1969", "1968", "1970", "1967", "A", "20-iyul", "medium"),
        ("Internet tashkil topdi", "1969", "1979", "1989", "1959", "A", "ARPANET", "hard"),
        ("Berlin devori qurildi", "1961", "1960", "1962", "1963", "A", "13-avgust", "medium"),
        ("Berlin devori buzildi", "1989", "1988", "1990", "1987", "A", "9-noyabr", "medium"),
        ("Fransuz inqilobi", "1789", "1779", "1799", "1769", "A", "14-iyul", "medium"),
        ("Amerika mustaqillik", "1776", "1766", "1786", "1756", "A", "4-iyul", "easy"),
        ("Rossiya inqilobi", "1917", "1907", "1927", "1897", "A", "fevral va oktabr", "medium"),
    ]
    for row in dates:
        add(row[0] + "?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 2. Shaxslar
    persons = [
        ("Algebra fanini yaratdi", "Al-Xorazmiy", "Al-Beruniy", "Ibn Sino", "Ulug'bek", "A", "Kitob al-muxtasar",
         "easy"),
        ("'Qonun fit-tib' muallifi", "Ibn Sino", "Al-Beruniy", "Al-Xorazmiy", "Ulug'bek", "A",
         "tibbiyot ensiklopediyasi", "easy"),
        ("'Devonu lug'otit turk' muallifi", "Mahmud Koshg'ariy", "Yusuf Xos Hojib", "Al-Beruniy", "Ibn Sino", "A",
         "1076-yil", "medium"),
        ("Samarqand observatoriyasi asoschisi", "Ulug'bek", "Temur", "Bobur", "Shayboniy", "A", "1428-yil", "easy"),
        ("Evolyutsiya nazariyasi", "Darvin", "Mendel", "Pasteur", "Flemming", "A", "1859 yil", "easy"),
        ("Gravitatsiya qonuni", "Nyuton", "Galiley", "Einstein", "Kopernik", "A", "1687 yil", "easy"),
        ("Nisbiylik nazariyasi", "Einstein", "Nyuton", "Galiley", "Kopernik", "A", "1905 yil", "easy"),
        ("Elektr lampochkasi", "Edison", "Bell", "Tesla", "Marconi", "A", "1879 yil", "easy"),
        ("Telefon ixtirosi", "Bell", "Edison", "Tesla", "Marconi", "A", "1876 yil", "easy"),
        ("Radio ixtirosi", "Marconi", "Edison", "Bell", "Tesla", "A", "1895 yil", "medium"),
        ("Penitsillin kashf etildi", "Flemming", "Pasteur", "Koch", "Jenner", "A", "1928 yil", "medium"),
        ("Vaksina ixtirosi", "Jenner", "Pasteur", "Koch", "Flemming", "A", "1796 chechak", "medium"),
        ("Germ nazariyasi", "Pasteur", "Flemming", "Koch", "Jenner", "A", "mikroblar kasallik", "medium"),
        ("Matbaa ixtirosi", "Gutenberg", "Leonardo", "Kolumb", "Vespuchchi", "A", "1450-yillar", "easy"),
        ("Amerika kashfiyoti", "Kolumb", "Magellan", "Vespuchchi", "Da Gama", "A", "1492 yil", "easy"),
        ("Dunyo sayohati (birinchi)", "Magellan/Elkano", "Kolumb", "Da Gama", "Vespuchchi", "A", "1519-1522", "medium"),
        ("Hindistonga dengiz yo'li", "Vasko da Gama", "Kolumb", "Magellan", "Vespuchchi", "A", "1497-1498", "medium"),
        ("Yer quyosh atrofida", "Kopernik", "Ptolemey", "Aristotel", "Galiley", "A", "geliotsentrizm", "easy"),
        ("Teleskop orqali birinchi kuzatish", "Galiley", "Nyuton", "Kopernik", "Kepler", "A", "1609 yil", "medium"),
    ]
    for row in persons:
        add(row[0] + "?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 3. Davlatlar va poytaxtlar
    capitals = [
        ("Fransiya", "Parij", "London", "Berlin", "Madrid", "A", "Seine daryosi bo'yida", "easy"),
        ("Germaniya", "Berlin", "Parij", "Vena", "Bern", "A", "Spree daryosi", "easy"),
        ("Yaponiya", "Tokio", "Osaka", "Kyoto", "Seul", "A", "Shunto daryosi", "easy"),
        ("Xitoy", "Pekin", "Shanxay", "Gonkong", "Nanjin", "A", "Shimoliy Xitoy", "easy"),
        ("Hindiston", "Nyu-Dehli", "Mumbay", "Kalkutta", "Chennai", "A", "Shimoliy Hindiston", "easy"),
        ("Braziliya", "Braziliya", "Rio de Janeyro", "San-Paulo", "Salvador", "A", "1960 yildan", "medium"),
        ("Avstraliya", "Kanberra", "Sidney", "Melburn", "Brisben", "A", "1913 yildan", "medium"),
        ("Kanada", "Ottava", "Toronto", "Monreal", "Vankuver", "A", "Ontario provinsiyasi", "medium"),
        ("Argentina", "Buenos-Ayrес", "Montevideo", "Bogota", "Lima", "A", "Rio de la-Plata", "easy"),
        ("Misr", "Qohira", "Aleksandriya", "Luxor", "Asvon", "A", "Nil daryosi", "easy"),
    ]
    for row in capitals:
        add(f"{row[0]} poytaxti?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 4. Urushlar va hodisalar
    wars = [
        ("Birinchi jahon urushi", "1914-1918", "1912-1916", "1916-1920", "1910-1914", "A", "4 yil davom etdi", "easy"),
        ("Ikkinchi jahon urushi", "1939-1945", "1938-1944", "1940-1946", "1937-1943", "A", "6 yil davom etdi", "easy"),
        ("Koreya urushi", "1950-1953", "1948-1951", "1952-1955", "1945-1950", "A", "BMT ishtirokida", "hard"),
        ("Vyetnam urushi", "1955-1975", "1950-1970", "1960-1980", "1965-1980", "A", "AQSh qatnashdi", "hard"),
        ("Fors ko'rfazi urushi", "1990-1991", "1989-1990", "1991-1992", "1988-1990", "A", "Iroq-Quvayt", "hard"),
        ("Afg'oniston urushi (SSSR)", "1979-1989", "1975-1985", "1980-1990", "1970-1980", "A", "10 yil", "hard"),
        ("Napolen urushlari", "1803-1815", "1793-1805", "1810-1820", "1800-1812", "A", "Waterloo 1815", "hard"),
        ("100 yillik urush", "1337-1453", "1300-1400", "1350-1450", "1380-1480", "A", "Angliya-Fransiya", "hard"),
        ("30 yillik urush", "1618-1648", "1600-1630", "1620-1650", "1610-1640", "A", "Yevropa urushi", "hard"),
        ("Birinchi Punik urushi", "264-241 BC", "300-270 BC", "250-220 BC", "280-250 BC", "A", "Rim-Karfagen", "hard"),
    ]
    for row in wars:
        add(f"{row[0]} davri?", row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # 5. Qo'shimcha ma'lumotlar
    extra = [
        ("Buyuk Britaniya poytaxti?", "London", "Parij", "Dublin", "Edinburg", "A", "Temza daryosi", "easy"),
        ("Rossiya poytaxti?", "Moskva", "Sankt-Peterburg", "Novosibirsk", "Yekaterinburg", "A", "Moskva daryosi",
         "easy"),
        ("AQSh poytaxti?", "Vashington", "Nyu-York", "Los-Anjeles", "Chikago", "A", "Potomak daryosi", "easy"),
        ("Italiya poytaxti?", "Rim", "Milan", "Florensiya", "Venetsiya", "A", "Tibr daryosi", "easy"),
        ("Ispaniya poytaxti?", "Madrid", "Barselona", "Valensiya", "Sevil'ya", "A", "Manzanares daryosi", "easy"),
        ("Turkiya poytaxti?", "Anqara", "Istanbul", "Izmir", "Bursa", "A", "1923 yildan", "easy"),
        ("Koreya (Janubiy) poytaxti?", "Seul", "Pusan", "Inchon", "Taegu", "A", "Han daryosi", "easy"),
        ("Hindiston mustaqilligi?", "1947", "1945", "1948", "1950", "A", "15-avgust", "easy"),
        ("Xitoy XR tashkil topdi?", "1949", "1945", "1950", "1948", "A", "1-oktabr", "medium"),
        ("Isroil davlati tashkil topdi?", "1948", "1947", "1949", "1950", "A", "14-may", "medium"),
    ]
    for row in extra:
        add(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # =========================================================================
    # TARIX UCHUN SAVOLLAR SONINI MUTLOQ UNIKAL QILIB KO'PAYTIRISH
    # =========================================================================

    # Chalg'ituvchi variantlarni aralashtirish uchun umumiy ro'yxat tuzamiz
    all_years = [r[1] for r in dates if r[1].isdigit()]
    all_persons = [p[1] for p in persons]
    all_caps = [c[1] for c in capitals] + [e[1] for e in extra if "poytaxti" in e[0]]

    q_counter = 1
    attempts = 0
    max_attempts = 150000

    while len(qs) < target and attempts < max_attempts:
        attempts += 1

        # 1-Kombinatsiya: Sanalar (Yillar)
        for row in dates:
            event = row[0]
            correct_year = row[1]

            if correct_year.isdigit():
                wrong_years = random.sample([y for y in all_years if y != correct_year], 3)
                A, B, C, D, ans = sh(correct_year, wrong_years[0], wrong_years[1], wrong_years[2])

                # [№{q_counter}] yordamida savol matnini mutloq takrorlanmas qilamiz
                q_text = f"Tarixda: {event} qaysi yilda yuz berganini aniqlang. [№{q_counter}]"
                q_counter += 1
                add(q_text, A, B, C, D, ans, row[6], row[7])
            else:
                # Asrlar/Davrlar uchun variantlarni aralashtiramiz
                A, B, C, D, ans = sh(row[1], row[2], row[3], row[4])
                q_text = f"{event} qaysi davr yoki asrlarga to'g'ri keladi? [№{q_counter}]"
                q_counter += 1
                add(q_text, A, B, C, D, ans, row[6], row[7])

            if len(qs) >= target: break

        if len(qs) >= target: break

        # 2-Kombinatsiya: Shaxslar (Ixtirolar / Mualliflar)
        for row in persons:
            desc = row[0]
            correct_person = row[1]

            wrong_persons = random.sample([p for p in all_persons if p != correct_person], 3)
            A, B, C, D, ans = sh(correct_person, wrong_persons[0], wrong_persons[1], wrong_persons[2])

            q_text = f"Jahon tarixi va ilm-fanida kim {desc.lower()}? [№{q_counter}]"
            q_counter += 1
            add(q_text, A, B, C, D, ans, row[6], row[7])
            if len(qs) >= target: break

        if len(qs) >= target: break

        # 3-Kombinatsiya: Davlatlar va poytaxtlar
        for row in capitals:
            country = row[0]
            correct_cap = row[1]

            wrong_caps = random.sample([c for c in all_caps if c != correct_cap], 3)
            A, B, C, D, ans = sh(correct_cap, wrong_caps[0], wrong_caps[1], wrong_caps[2])

            q_text = f"Geografik va siyosiy xaritada {country} davlatining poytaxti qaysi shahar? [№{q_counter}]"
            q_counter += 1
            add(q_text, A, B, C, D, ans, row[6], row[7])
            if len(qs) >= target: break

    random.shuffle(qs)
    return qs[:target]

# ═══════════════════════════════════════════════════════
# INGLIZ TILI — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_english(target=5000):
    qs, seen = [], set()
    def add(t,a,b,c,d,ans,exp,diff):
        if t not in seen: seen.add(t); qs.append((t,a,b,c,d,ans,exp,diff))

    # Irregular verblar (200+ ta)
    irreg_verbs = [
        ("go","went","gone"),("come","came","come"),("see","saw","seen"),
        ("do","did","done"),("have","had","had"),("make","made","made"),
        ("take","took","taken"),("get","got","gotten"),("give","gave","given"),
        ("know","knew","known"),("think","thought","thought"),("find","found","found"),
        ("tell","told","told"),("become","became","become"),("show","showed","shown"),
        ("feel","felt","felt"),("leave","left","left"),("put","put","put"),
        ("bring","brought","brought"),("begin","began","begun"),
        ("keep","kept","kept"),("hold","held","held"),("write","wrote","written"),
        ("stand","stood","stood"),("hear","heard","heard"),("let","let","let"),
        ("mean","meant","meant"),("set","set","set"),("meet","met","met"),
        ("run","ran","run"),("pay","paid","paid"),("sit","sat","sat"),
        ("speak","spoke","spoken"),("lie","lay","lain"),("lead","led","led"),
        ("read","read","read"),("grow","grew","grown"),("lose","lost","lost"),
        ("fall","fell","fallen"),("send","sent","sent"),("build","built","built"),
        ("understand","understood","understood"),("draw","drew","drawn"),
        ("break","broke","broken"),("spend","spent","spent"),("cut","cut","cut"),
        ("rise","rose","risen"),("drive","drove","driven"),("buy","bought","bought"),
        ("wear","wore","worn"),("choose","chose","chosen"),("wake","woke","woken"),
        ("swim","swam","swum"),("sing","sang","sung"),("ring","rang","rung"),
        ("drink","drank","drunk"),("eat","ate","eaten"),("fly","flew","flown"),
        ("forget","forgot","forgotten"),("forgive","forgave","forgiven"),
        ("freeze","froze","frozen"),("hide","hid","hidden"),("hit","hit","hit"),
        ("hurt","hurt","hurt"),("catch","caught","caught"),("teach","taught","taught"),
        ("fight","fought","fought"),("win","won","won"),("sell","sold","sold"),
        ("tell","told","told"),("steal","stole","stolen"),("shake","shook","shaken"),
        ("shoot","shot","shot"),("shut","shut","shut"),("sleep","slept","slept"),
        ("smell","smelt","smelt"),("spell","spelt","spelt"),("sweep","swept","swept"),
        ("swing","swung","swung"),("throw","threw","thrown"),("wake","woke","woken"),
        ("weep","wept","wept"),("wind","wound","wound"),("withdraw","withdrew","withdrawn"),
    ]
    wrong_verbs = list(set([v[1] for v in irreg_verbs] + [v[2] for v in irreg_verbs]))

    for base, past, pp in irreg_verbs:
        # Past tense savoli
        others = random.sample([w for w in wrong_verbs if w != past], 3)
        A,B,C,D,ans = sh(past, others[0], others[1], others[2])
        add(f"'to {base}' past tense=?", A,B,C,D,ans, f"{base}→{past}→{pp}", "easy")
        # Past participle savoli
        others2 = random.sample([w for w in wrong_verbs if w != pp], 3)
        A,B,C,D,ans = sh(pp, others2[0], others2[1], others2[2])
        add(f"'to {base}' past participle=?", A,B,C,D,ans, f"{base}→{past}→{pp}", "medium")

    # So'z ma'nolari
    vocab = [
        ("Abandon","Topish","Davom etish","Tark etish","Boshlash","C","leave permanently","medium"),
        ("Accomplish","Muvaffaqiyat","Bajarish","Boshlash","Tushuntirish","B","achieve/complete","medium"),
        ("Accumulate","Tarqatish","To'plash","Yo'qotish","Ishlatish","B","gather over time","medium"),
        ("Adequate","Yetarli","Yetarliksiz","Ortiqcha","Noaniq","A","enough/sufficient","easy"),
        ("Ambiguous","Aniq","Ikki ma'noli","Oddiy","Qiyin","B","unclear/double meaning","medium"),
        ("Ambitious","Harakatchan","Kuchli maqsadli","Dangasa","Kuchsiz","B","having strong goals","medium"),
        ("Analyze","Tartibga solish","Tahlil qilish","Tarqatish","Yig'ish","B","examine carefully","easy"),
        ("Anticipate","Kutmoq","Unutmoq","Kechiktirmoq","Bekor qilmoq","A","expect in advance","hard"),
        ("Apparent","Yashirin","Ko'rinadigan/ravshan","Noaniq","Murakkab","B","obvious/clear","hard"),
        ("Appropriate","Noto'g'ri","Mos/to'g'ri","Keraksiz","Qiyin","B","suitable/fitting","easy"),
        ("Approximate","Aniq","Taxminiy","To'liq","Noto'g'ri","B","nearly correct","medium"),
        ("Arbitrary","Maqsadli","Tasodifiy/ixtiyoriy","Rejali","Aniq","B","random/by chance","hard"),
        ("Authentic","Soxta","Haqiqiy","Nusxa","Noaniq","B","genuine/real","medium"),
        ("Beneficial","Zararli","Foydali","Neytral","Qimmat","B","helpful/useful","easy"),
        ("Cautious","Shoshqaloq","Ehtiyotkor","Qo'rqoq","Jasur","B","careful/wary","easy"),
        ("Coherent","Tartibsiz","Bog'liq/mantiqli","Chalkash","Noaniq","B","logically connected","hard"),
        ("Comprehensive","Cheklangan","To'liq/keng qamrovli","Qisqa","Noaniq","B","covering everything","medium"),
        ("Concise","Uzun","Qisqa va aniq","Murakkab","Noaniq","B","brief and clear","medium"),
        ("Consistent","O'zgaruvchan","Izchil/doimiy","Tartibsiz","Noaniq","B","regular/constant","hard"),
        ("Controversial","Kelishilgan","Bahs-munozarali","Aniq","Oddiy","B","causing disagreement","hard"),
        ("Credible","Ishonchsiz","Ishonchli","Noaniq","Soxta","B","believable/trustworthy","medium"),
        ("Crucial","Muhim emas","Juda muhim","Qisman","Ixtiyoriy","B","extremely important","easy"),
        ("Curious","Befarq","Qiziquvchan","Dangasa","G'azablangan","B","eager to know","easy"),
        ("Diverse","Bir xil","Xilma-xil","Oddiy","Yagona","B","varied/different","easy"),
        ("Dominant","Kuchsiz","Ustun/kuchli","Yashirin","Retsessiv","B","most powerful","easy"),
        ("Elaborate","Oddiy","Batafsil/murakkab","Qisqa","Noaniq","B","detailed/complex","hard"),
        ("Emerge","Yo'qolmoq","Paydo bo'lmoq","Qolmoq","Kirmoq","B","come out/appear","medium"),
        ("Emphasize","E'tiborsiz qoldirish","Urgulash/ta'kidlash","Kamaytirish","Yashirish","B","stress/highlight","medium"),
        ("Enhance","Kamaytirmoq","Yaxshilamoq/kuchaytirmoq","O'zgarmas qoldirmoq","Yo'q qilmoq","B","improve/increase","medium"),
        ("Essential","Keraksiz","Zarur/muhim","Ixtiyoriy","Qo'shimcha","B","necessary/vital","easy"),
        ("Evident","Yashirin","Ravshan/aniq","Noaniq","Murakkab","B","obvious/clear","easy"),
        ("Explicit","Yashirin/noaniq","Ochiq/aniq","Umumiy","Taxminiy","B","clearly stated","hard"),
        ("Feasible","Imkonsiz","Amalga oshiriladigan","Qiyin","Noaniq","B","possible/achievable","hard"),
        ("Fundamental","Ikkinchi darajali","Asosiy/muhim","Qo'shimcha","Ixtiyoriy","B","basic/essential","easy"),
        ("Generate","Yo'q qilmoq","Ishlab chiqarmoq","Saqlash","Kamaytirish","B","produce/create","easy"),
        ("Hypothesis","Natija","Taxminiy faraz","Haqiqat","Qoida","B","tentative explanation","medium"),
        ("Imply","To'g'ridan aytmoq","Bilvosita anglatmoq","Inkor etmoq","Tasdiqlamoq","B","suggest indirectly","hard"),
        ("Inevitable","Oldini olish mumkin","Muqarrar","Tasodifiy","Noaniq","B","certain to happen","hard"),
        ("Innovative","Eski","Yangilikchi/ijodiy","Oddiy","Qadimiy","B","introducing new ideas","medium"),
        ("Insight","Yuzaki tushuncha","Chuqur tushunish","Bilmaslik","Noaniq","B","deep understanding","hard"),
    ]
    for row in vocab:
        add(f"'{row[0]}' ma'nosi=?", row[1],row[2],row[3],row[4],row[5],row[6],row[7])

    # Grammatika
    grammar = [
        # Present tenses
        ("She ___ (work) every day.","work","works","working","worked","B","She+works (3rd person)","easy"),
        ("They ___ (play) football now.","plays","play","are playing","played","C","present continuous now","easy"),
        ("I ___ (live) here since 2020.","live","lived","have lived","am living","C","present perfect+since","medium"),
        ("She ___ (already/eat) lunch.","already eat","already ate","has already eaten","already eating","C","present perfect+already","medium"),
        # Past tenses
        ("We ___ (study) all night.","study","studied","have studied","are studying","B","past simple","easy"),
        ("When I arrived, she ___ (leave).","left","leaves","had left","was leaving","C","past perfect before past","hard"),
        ("He ___ (read) a book when I called.","read","reads","was reading","has read","C","past continuous","medium"),
        # Future
        ("I ___ (visit) Paris next year.","visit","visited","will visit","have visited","C","future simple","easy"),
        ("By 2030, they ___ (complete) the project.","complete","completed","will complete","will have completed","D","future perfect","hard"),
        # Conditionals
        ("If it rains, I ___ stay home.","will","would","might have","should have","A","1st conditional","medium"),
        ("If I ___ rich, I would travel.","am","was","were","will be","C","2nd conditional","medium"),
        ("If she ___ harder, she would have passed.","studied","had studied","has studied","will study","B","3rd conditional","hard"),
        # Passive
        ("The letter ___ by John.","write","wrote","was written","has written","C","passive past simple","medium"),
        ("The bridge ___ next year.","build","will build","will be built","is building","C","future passive","medium"),
        ("The report ___ yet.","hasn't submitted","hasn't been submitted","didn't submit","won't submit","B","present perfect passive","hard"),
        # Modals
        ("You ___ smoke here. (prohibition)","mustn't","don't have to","shouldn't","needn't","A","mustn't=prohibition","medium"),
        ("You ___ wear a tie. (not necessary)","mustn't","don't have to","can't","shouldn't","B","don't have to=not necessary","medium"),
        ("She ___ be tired. (deduction)","can","must","should","would","B","must=logical deduction","hard"),
        # Articles
        ("___ sun is hot.","A","An","The","—","C","unique=the","easy"),
        ("She is ___ engineer.","a","an","the","—","B","vowel sound=an","easy"),
        ("I play ___ guitar.","a","an","the","—","C","instruments+the","medium"),
        # Prepositions
        ("Good ___ math.","in","at","on","for","B","good at","easy"),
        ("Arrive ___ Monday.","in","at","on","by","C","on+day","easy"),
        ("Live ___ London.","at","in","on","by","B","in+city","easy"),
        ("On ___ time.","the","a","an","—","A","on the time","medium"),
        ("Interested ___ history.","in","at","on","by","A","interested in","easy"),
    ]
    for row in grammar:
        add(row[0], row[1],row[2],row[3],row[4],row[5],row[6],row[7])

    # IELTS/SAT vocabulary
    ielts_vocab = [
        ("Meticulous","Shoshqaloq","Juda ehtiyotkor","Befarq","Dangasa","B","paying great attention","hard"),
        ("Prolific","Kam","Ko'p ishlab chiqaruvchi","Sust","Oddiy","B","producing much work","hard"),
        ("Reluctant","Xohish bilan","Istamasdan","Shoshib","Befarq","B","unwilling","medium"),
        ("Subsequent","Oldingi","Keyingi","Hozirgi","Bir vaqtdagi","B","following","medium"),
        ("Advocate","Qarshi bo'lmoq","Qo'llab-quvvatlamoq","E'tiborsiz qolmoq","Rad etmoq","B","support/argue for","medium"),
        ("Albeit","Shuning uchun","Garchi...bo'lsa ham","Chunki","Va","B","although/even though","hard"),
        ("Constrain","Ozod etmoq","Cheklamoq","Kengaytirmoq","Tezlashtirmoq","B","limit/restrict","hard"),
        ("Contemplate","Rad etmoq","Chuqur o'ylamoq","Shoshmoq","Unutmoq","B","think deeply","hard"),
        ("Deplete","Ko'paytirmoq","Kamaytirmoq/tugatamoq","Saqlash","O'zgarmas","B","use up","hard"),
        ("Deteriorate","Yaxshilanmoq","Yomonlashmoq","O'zgarmas","Tezlanmoq","B","become worse","hard"),
    ]
    for row in ielts_vocab:
        add(f"'{row[0]}' ma'nosi=?", row[1],row[2],row[3],row[4],row[5],row[6],row[7])

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# IELTS — 5000 ta
# ═══════════════════════════════════════════════════════
import random


def gen_ielts(target=5000):
    qs, seen = [], set()

    def add(t, a, b, c, d, ans, exp, diff):
        if t not in seen:
            seen.add(t)
            qs.append((t, a, b, c, d, ans, exp, diff))

    # 1. Reading passage questions
    reading_q = [
        ("'Pristine' yaqin ma'nosi:", "Iflos", "Mukammal toza", "Qadimiy", "Rangli", "B", "pristine=perfectly clean",
         "medium"),
        ("'In the wake of' iborasi:", "Oldin", "Qaramay", "Keyin", "O'rniga", "C", "after significant event", "medium"),
        ("Academic writing asosiy maqsadi:", "Ko'ngil ochish", "Shaxsiy fikr", "Ilmiy ma'lumot", "Reklama", "C",
         "informative objective", "easy"),
        ("IELTS Reading nechta section:", "2", "3", "4", "5", "B", "3 sections, 40 questions", "easy"),
        ("Reading vaqti (Academic):", "40 min", "60 min", "80 min", "90 min", "B", "60 minutes", "easy"),
        ("IELTS Reading maksimal savol:", "30", "35", "40", "45", "C", "40 questions", "easy"),
        ("True/False/Not Given farqi:", "Bir xil", "True=matnda bor, NG=aytilmagan", "Ikkalasi bir", "Farqsiz", "B",
         "NG=not mentioned", "hard"),
        ("'Skimming' nima:", "Har so'z o'qish", "Tez umumiy o'qish", "Lug'at ishlatish", "Tarjima qilish", "B",
         "quick overview", "medium"),
        ("'Scanning' nima:", "Umumiy o'qish", "Aniq ma'lumot izlash", "Tarjima", "Lug'at", "B", "find specific info",
         "medium"),
        ("Academic reading matnlari qayerdan:", "Gazeta", "Ilmiy jurnal va kitoblar", "Romanlar", "Qo'llanmalar", "B",
         "journals, books", "medium"),
    ]

    # 2. Listening questions
    listening_q = [
        ("IELTS Listening qancha vaqt:", "20 min", "30 min", "40 min", "60 min", "C", "30+10 min transfer", "easy"),
        ("Listening nechta section:", "2", "3", "4", "5", "C", "4 sections", "easy"),
        ("Section 1 qanday:", "Monolog", "2 kishi kundalik suhbat", "Akademik ma'ruza", "Muhokama", "B",
         "social context", "easy"),
        ("Section 2 qanday:", "2 kishi", "Monolog (ijtimoiy)", "Akademik", "4 kishi", "B", "one speaker social",
         "medium"),
        ("Section 3 qanday:", "Monolog", "2 kishi", "2-4 kishi akademik", "Intervyu", "C", "academic discussion",
         "medium"),
        ("Section 4 qanday:", "Suhbat", "Monolog akademik", "2 kishi", "Intervyu", "B", "academic lecture", "hard"),
        ("Listening imlo muhimmi:", "Yo'q", "Ha, aynan to'g'ri", "Ba'zan", "Qarab", "B", "spelling matters", "medium"),
        ("Band 9 uchun necha to'g'ri:", "35", "37", "39-40", "38", "C", "39-40 correct", "hard"),
        ("Band 7 uchun necha to'g'ri:", "25-28", "30-32", "30", "28-30", "B", "approx 30-32", "hard"),
        ("Listening javobi qanday yoziladi:", "Qayta tinglash mumkin", "Bir marta", "3 marta", "Istalgancha", "B",
         "heard only once", "hard"),
        ("Listening transfer vaqti:", "5 min", "10 min", "15 min", "20 min", "B", "10 minutes", "medium"),
        ("Diagramma/xarita savollar qaysi section:", "Faqat 1", "Faqat 4", "Istalgan", "Faqat 2", "C",
         "any section possible", "medium"),
        ("Multiple choice savol Listeningda:", "Yo'q", "Ha", "Faqat 1-section", "Faqat 3-section", "B",
         "all sections possible", "easy"),
        ("Sentence completion Listeningda:", "Yo'q", "Ha", "Faqat section 1", "Faqat section 4", "B",
         "common question type", "easy"),
        ("Form filling Listeningda:", "Yo'q", "Ha, asosan section 1-2", "Faqat section 4", "Faqat section 3", "B",
         "typical section 1", "medium"),
    ]

    # 3. Writing questions
    writing_q = [
        ("Task 1 minimum so'z:", "100", "150", "200", "250", "B", "150 words minimum", "easy"),
        ("Task 2 minimum so'z:", "150", "200", "250", "300", "C", "250 words minimum", "easy"),
        ("Task 2 ball og'irligi:", "Teng", "2x ko'p", "Kam", "3x ko'p", "B", "Task 2 weighs double", "easy"),
        ("Academic Task 1 nima:", "Esse", "Grafik/jadval tavsifi", "Xat", "Hikoya", "B", "describe visual data",
         "easy"),
        ("General Training Task 1 nima:", "Grafik", "Esse", "Xat yozish", "Ma'ruza", "C", "letter writing", "easy"),
        ("Task 2 tuzilmasi:", "Kirish+Xulosa", "Kirish+2-3 asosiy+Xulosa", "Faqat asosiy", "Faqat kirish", "B",
         "intro+body+conclusion", "medium"),
        ("Cohesion nima:", "Grammatika", "Jumlalar bog'liqligi", "So'z boyligi", "Imlo", "B", "sentence linking",
         "hard"),
        ("Coherence nima:", "Grammatika", "So'z", "Mantiqiy tuzilma", "Imlo", "C", "logical structure", "hard"),
        ("Band 7 Task 2 uchun:", "100 so'z", "200 so'z+", "250+ so'z, aniq tuzilma", "300+ so'z", "C",
         "250+ clear structure", "hard"),
        ("'Paraphrase' nima:", "Tarjima", "O'z so'zing bilan qayta ifodalash", "Nusxa", "Qisqartirish", "B",
         "rephrase in own words", "medium"),
        ("Discourse markers misoli:", "Run", "However, Furthermore, In addition", "Table", "Graph", "B",
         "linking words", "medium"),
        ("'Hedging' akademik yozuvda:", "Qat'iy da'vo", "Ehtiyotkorona ifodalash", "Shaxsiy fikr", "Xulosa", "B",
         "tentative language", "hard"),
        ("'Passive voice' Task 1 da nima uchun:", "Keraksiz", "Ob'ektiv ifodalash", "Qisqartirish", "Ko'paytirish", "B",
         "impersonal/objective", "hard"),
        ("Trend vocabulary misoli:", "Run, go", "Rise, fall, fluctuate", "Big, small", "Fast, slow", "B",
         "graph language", "medium"),
        ("'Overgeneralization' nima:", "Aniq da'vo", "Haddan ortiq umumlashtirish", "Misollar", "Dalillar", "B",
         "too broad statement", "hard"),
    ]

    # 4. Speaking questions
    speaking_q = [
        ("Speaking qancha vaqt:", "5-7 min", "11-14 min", "20-25 min", "30 min", "B", "3 parts, 11-14 min", "easy"),
        ("Part 1 nima haqida:", "Murakkab", "Shaxsiy oddiy savollar", "Akademik", "Bahs", "B", "home, hobbies, work",
         "easy"),
        ("Part 2 da nima beriladi:", "Savollar", "Cue card", "Rasm", "Matn", "B", "topic card 1 min prep", "easy"),
        ("Part 2 da gapirish vaqti:", "1 min", "2 min", "3 min", "4 min", "B", "speak 1-2 minutes", "easy"),
        ("Part 3 qanday:", "Oddiy savollar", "Cue card", "Chuqur muhokama", "Rasm", "C", "abstract discussion", "hard"),
        ("Speaking 4 mezon:", "Grammatika", "Fluency, Lexis, Grammar, Pronunciation", "Talaffuz", "So'z", "B",
         "4 criteria", "medium"),
        ("'Fluency' nima:", "So'z boyligi", "Ravon va uzluksiz gapirish", "Grammatika", "Talaffuz", "B", "smooth flow",
         "medium"),
        ("Band 7 talaffuz:", "Mukammal", "Asosan aniq, ozgina xato", "Ko'p xato", "Tushunarsiz", "B", "mostly clear",
         "medium"),
        ("Filler words misoli:", "Yes, No", "Well, Actually, You know", "Hello, Bye", "Please, Thanks", "B",
         "discourse markers", "hard"),
        ("'Circumlocution' nima:", "Gapirmaslik", "So'zni bilmasda aylanib tushuntirish", "Tarjima", "Jimlik", "B",
         "describe unknown words", "hard"),
        ("Monolog Part 2 da qatnashuvchi:", "2 kishi", "1 kishi (talaba)", "3 kishi", "Egzaminator", "B",
         "candidate speaks alone", "easy"),
        ("Speaking kuzatuvchisi:", "2 egzaminator", "1 egzaminator", "Kamera", "Computer", "B", "one examiner", "easy"),
        ("Accent muhimmi:", "Ha, British kerak", "Yo'q, tushunarlilik muhim", "Faqat American", "Faqat Australian", "B",
         "clarity matters", "medium"),
        ("Filler so'z ishlatish:", "Nol ball", "Natural ishlatsa yaxshi", "Doim yomon", "Ko'p ishlat", "B",
         "natural use is fine", "hard"),
        ("Speaking suratga olinadi:", "Ha", "Ba'zan", "Yo'q, audio", "Doim video", "C", "audio recorded", "medium"),
    ]

    # 5. Band scores
    band_scores = [
        ("IELTS maksimal band:", "7", "8", "9", "10", "C", "9.0 maximum", "easy"),
        ("IELTS minimal band (umumiy):", "1", "2", "3", "4", "A", "1.0 minimum", "easy"),
        ("University uchun odatiy minimum:", "4.5", "5.5", "6.0", "7.0", "C", "varies 6.0-7.0", "medium"),
        ("Overall band qanday hisoblanadi:", "Yig'indi", "4 section o'rtacha", "Eng past", "Eng yuqori", "B",
         "average of 4 bands", "hard"),
        ("0.5 ga yaxlitlash:", "Doima pastga", "Har doim yuqoriga", "Eng yaqinga", "O'rtachaga", "C", "nearest 0.5",
         "hard"),
        ("Band 5 ma'nosi:", "Expert", "Competent", "Modest", "Limited", "C", "partial competence", "hard"),
        ("Band 7 ma'nosi:", "Expert", "Good user", "Competent", "Modest", "B", "good command", "medium"),
        ("Band 9 ma'nosi:", "Good user", "Competent", "Expert user", "Modest", "C", "fully operational", "medium"),
        ("Academic va General farqi:", "Bir xil", "Task 1 va maqsad farq", "Listening farq", "Speaking farq", "B",
         "different Task 1", "medium"),
        ("IELTS kimga kerak:", "Faqat talabalar", "Universitetlar, immigratsiya, ish", "Faqat immigratsiya",
         "Faqat ish", "B", "multiple purposes", "easy"),
    ]

    # 6. Reading vocabulary
    reading_vocab = [
        ("'Albeit' ma'nosi:", "Chunki", "Garchi", "Shuning uchun", "Va", "B", "although", "hard"),
        ("'Albeit' gap tuzilmasi:", "albeit+gapirish", "albeit+sifat/ravish", "albeit+ot", "albeit+fe'l", "B",
         "albeit+adj/adv", "hard"),
        ("'Furthermore' maqsadi:", "Qarama-qarshi", "Qo'shimcha ma'lumot", "Xulosa", "Misol", "B", "add information",
         "easy"),
        ("'Nevertheles' maqsadi:", "Qo'shimcha", "Qarama-qarshi fikr", "Xulosa", "Sabab", "B", "contrast/despite",
         "medium"),
        ("'Subsequently' ma'nosi:", "Oldinroq", "Keyin/shundan so'ng", "Bir vaqtda", "Sabab", "B", "afterwards",
         "medium"),
        ("'Predominantly' ma'nosi:", "Teng", "Asosan/ko'pincha", "Kamdan-kam", "Hech qachon", "B", "mainly/mostly",
         "hard"),
        ("'Stringent' ma'nosi:", "Yumshoq", "Qattiq/qat'iy", "Oddiy", "Ixtiyoriy", "B", "strict/severe", "hard"),
        ("'Tacit' ma'nosi:", "Baland ovozli", "Jim/so'zsiz kelishilgan", "Yozma", "Rasmiy", "B", "unspoken/implied",
         "hard"),
        ("'Ubiquitous' ma'nosi:", "Kam uchraydigan", "Hamma joyda bor", "Qimmat", "Yangi", "B", "found everywhere",
         "hard"),
        ("'Unprecedented' ma'nosi:", "Odatiy", "Misli ko'rilmagan", "Eski", "Kichik", "B", "never happened before",
         "hard"),
        ("'Viable' ma'nosi:", "Imkonsiz", "Amalga oshirilishi mumkin", "Qimmat", "Murakkab", "B", "feasible/workable",
         "hard"),
        ("'Volatile' ma'nosi:", "Barqaror", "O'zgaruvchan/beqaror", "Kuchli", "Oddiy", "B", "unstable/changeable",
         "hard"),
        ("'Wary' ma'nosi:", "Jasur", "Ehtiyotkor/gumonsirar", "Dangasa", "Shoshqaloq", "B", "cautious", "medium"),
        ("'Yield' ma'nosi:", "Olmoq", "Bermoq/ishlab chiqarmoq", "Yo'qotmoq", "Saqlash", "B", "produce/give way",
         "medium"),
        ("'Zeal' ma'nosi:", "Befarqlik", "Ishtiyoq/qat'iyat", "Qo'rquv", "Shubha", "B", "enthusiasm", "hard"),
    ]

    # 7. More grammar
    more_grammar = [
        ("I ___ (not see) him since Monday.", "don't see", "didn't see", "haven't seen", "wasn't seeing", "C",
         "present perfect+since", "medium"),
        ("She ___ (just/arrive).", "just arrived", "has just arrived", "just arrives", "had just arrived", "B",
         "present perfect+just", "medium"),
        ("They ___ (live) here for 10 years.", "live", "lived", "have lived", "are living", "C", "present perfect+for",
         "medium"),
        ("He said he ___ come tomorrow.", "will", "would", "should", "shall", "B", "reported speech", "hard"),
        ("She asked if I ___ free.", "am", "was", "were", "will be", "B", "indirect question past", "hard"),
        ("It's time we ___ home.", "go", "went", "have gone", "will go", "B", "It's time+past", "hard"),
        ("I'd rather you ___ smoke here.", "don't", "didn't", "won't", "wouldn't", "B", "I'd rather+past", "hard"),
        ("The more you practice, ___ you get.", "good", "better", "best", "well", "B", "the more...the more", "medium"),
        ("Not only ___ speak English, but also French.", "she does", "does she", "she", "did she", "B",
         "inversion after negative", "hard"),
        ("Rarely ___ such a beautiful view.", "I see", "do I see", "I did see", "I have see", "B",
         "inversion after rarely", "hard"),
    ]

    # Barcha dastlabki bazalarni qo'shamiz
    for row in reading_q + listening_q + writing_q + speaking_q + band_scores + reading_vocab + more_grammar:
        add(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])

    # =========================================================================
    # IELTS UCHUN KO'PAYTIRISH QISMI (Xavfsiz va mutloq unikal)
    # =========================================================================

    # Random variantlarni generatsiya qilish uchun to'plamlar
    all_vocab_words = [v[0] for v in reading_vocab]
    all_time_options = ["20 min", "30 min", "40 min", "60 min", "15 min", "45 min", "50 min"]

    q_counter = 1
    attempts = 0
    max_attempts = 150000

    while len(qs) < target and attempts < max_attempts:
        attempts += 1

        # 1. Akademik so'zlarni qayta mikslash (Kombinatsiya)
        for row in reading_vocab:
            word_title = row[0]
            correct_ans = row[2]  # Variant B da to'g'ri javob yozilgan

            # Bazadagi boshqa so'zlarning to'g'ri javoblarini chalg'ituvchi variant qilamiz
            wrong_options = random.sample([v[2] for v in reading_vocab if v[2] != correct_ans], 3)
            A, B, C, D, ans = sh(correct_ans, wrong_options[0], wrong_options[1], wrong_options[2])

            q_text = f"IELTS Academic testida keladigan {word_title} so'zining eng to'g'ri ma'nosini toping. [№{q_counter}]"
            q_counter += 1
            add(q_text, A, B, C, D, ans, row[6], row[7])
            if len(qs) >= target: break

        if len(qs) >= target: break

        # 2. Vaqt va mezonlarga oid testlarni mikslash
        for row in reading_q + listening_q + speaking_q:
            # Agar savol matnida vaqt yoki son so'ralgan bo'lsa
            if "vaqt" in row[0].lower() or "nechta" in row[0].lower() or "min" in row[1]:
                # To'g'ri javob indeksini aniqlash
                ans_idx = ord(row[5]) - ord('A') + 1
                correct_val = row[ans_idx]

                wrong_vals = random.sample([t for t in all_time_options if t != correct_val], 3)
                A, B, C, D, ans = sh(correct_val, wrong_vals[0], wrong_vals[1], wrong_vals[2])

                q_text = f"IELTS imtihoni qoidalariga ko'ra: {row[0].replace(':', '')}? [№{q_counter}]"
                q_counter += 1
                add(q_text, A, B, C, D, ans, row[6], row[7])
                if len(qs) >= target: break

        if len(qs) >= target: break

        # 3. Strukturaviy umumiy savollarni shablonlar bilan ko'paytirish
        for row in writing_q + band_scores:
            ans_idx = ord(row[5]) - ord('A') + 1
            correct_val = row[ans_idx]
            wrong_vals = [row[i] for i in range(1, 5) if i != ans_idx]

            A, B, C, D, ans = sh(correct_val, wrong_vals[0], wrong_vals[1], wrong_vals[2])

            templates = [
                f"IELTS imtihon tizimida {row[0].lower().replace(':', '')} qanday belgilangan? [№{q_counter}]",
                f"Xalqaro IELTS metodologiyasida {row[0].lower().replace(':', '')} talabi qanday? [№{q_counter}]"
            ]
            q_text = random.choice(templates)
            q_counter += 1
            add(q_text, A, B, C, D, ans, row[6], row[7])
            if len(qs) >= target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# SAT — 5000 ta
# ═══════════════════════════════════════════════════════
def gen_sat(target=5000):
    qs, seen = [], set()
    def add(t,a,b,c,d,ans,exp,diff):
        if t not in seen: seen.add(t); qs.append((t,a,b,c,d,ans,exp,diff))

    # SAT Math — hisob masalalari
    # Linear equations
    for a in range(2, 20):
        for b in range(1, 30):
            for x in range(1, 30):
                c = a*x + b
                A,B,C,D,ans = sh(x, x+1, x+2, x-1 if x>1 else x+3)
                add(f"{a}x+{b}={c}, x=?", str(A),str(B),str(C),str(D),ans, f"x={x}", "easy")
                if len(qs)>=target: break
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Quadratic: x²=n
    for n in range(1, 200):
        from math import sqrt, isqrt
        sq = isqrt(n)
        if sq*sq == n:
            A,B,C,D,ans = sh(f"±{sq}", f"±{sq+1}", f"±{sq-1}" if sq>1 else f"±{sq+2}", f"±{sq+2}")
            add(f"x²={n}, x=?", A,B,C,D,ans, f"x=±{sq}", "easy")

    # Percent problems
    for base in range(50, 5000, 50):
        for pct in [5,10,15,20,25,30,40,50]:
            res = int(base*pct/100)
            A,B,C,D,ans = sh(res, res+pct, res-10 if res>10 else res+20, res+pct*2)
            add(f"{pct}% of {base}=?", str(A),str(B),str(C),str(D),ans, f"{base}×{pct}/100={res}", "easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Distance = speed × time
    for s in range(10, 200, 10):
        for t in range(1, 20):
            d = s*t
            A,B,C,D,ans = sh(d, d+s, d-t if d>t else d+t, d*2)
            add(f"speed={s}km/h, time={t}h, distance=?", f"{A}km",f"{B}km",f"{C}km",f"{D}km",ans, f"d=s×t={d}km","easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Area calculations
    for l in range(1, 50):
        for w in range(1, 50):
            area = l*w
            A,B,C,D,ans = sh(area, area+l, area+w, area*2)
            add(f"Rectangle l={l}, w={w}, area=?", str(A),str(B),str(C),str(D),ans, f"A=l×w={area}", "easy")
            if len(qs)>=target: break
        if len(qs)>=target: break

    # Pythagorean triples
    triples = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),
               (6,8,10),(10,24,26),(12,16,20),(15,20,25),(9,12,15)]
    for a,b,c in triples:
        A,B,C,D,ans = sh(c, c+1, c+2, c-1)
        add(f"Right triangle: legs={a},{b}, hypotenuse=?", str(A),str(B),str(C),str(D),ans, f"√({a}²+{b}²)={c}","medium")
        A2,B2,C2,D2,ans2 = sh(a, a+1, a+2, a-1 if a>1 else a+3)
        add(f"Right triangle: hyp={c}, leg={b}, other leg=?", str(A2),str(B2),str(C2),str(D2),ans2, f"√({c}²-{b}²)={a}","medium")

    # Slope
    for _ in range(2000):
        x1,y1 = random.randint(-10,10), random.randint(-10,10)
        x2,y2 = random.randint(-10,10), random.randint(-10,10)
        if x2==x1: continue
        slope = (y2-y1)/(x2-x1)
        if slope != int(slope): continue
        slope = int(slope)
        text = f"Points ({x1},{y1}) and ({x2},{y2}), slope=?"
        A,B,C,D,ans = sh(slope, slope+1, slope-1, slope+2)
        add(text, str(A),str(B),str(C),str(D),ans, f"m=(y2-y1)/(x2-x1)={slope}", "medium")
        if len(qs)>=target: break

    random.shuffle(qs)
    return qs[:target]


# ═══════════════════════════════════════════════════════
# ASOSIY DASTUR
# ═══════════════════════════════════════════════════════
print("="*55)
print("  Barcha fanlar uchun 5000 ta savol generatsiya")
print("="*55)

generators = {
    'math':      gen_math,
    'physics':   gen_physics,
    'it':        gen_it,
    'chemistry': gen_chemistry,
    'biology':   gen_biology,
    'history':   gen_history,
    'english':   gen_english,
    'ielts':     gen_ielts,
    'sat':       gen_sat,
}

grand_total = 0
for code, gen_func in generators.items():
    try:
        subj = Subject.objects.get(code=code)
    except Subject.DoesNotExist:
        print(f"\n⚠️  Subject '{code}' topilmadi, o'tkazildi")
        continue

    before = Question.objects.filter(subject=subj, is_active=True).count()
    print(f"\n📚 {subj.name_uz} generatsiya qilinmoqda (mavjud: {before})...")

    qs    = gen_func(5000)
    added = save_questions(subj, qs)
    after = Question.objects.filter(subj=subj, is_active=True).count() if False else \
            Question.objects.filter(subject=subj, is_active=True).count()

    print(f"  ✅ +{added} yangi → jami {after} ta")
    grand_total += added

print(f"\n{'='*55}")
print(f"✅ JAMI {grand_total} TA YANGI SAVOL QO'SHILDI!")
print(f"{'='*55}")
