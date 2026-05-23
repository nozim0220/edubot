import os, sys, django, random
from fractions import Fraction
from math import gcd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('USE_SQLITE', 'true')
django.setup()

from apps.education.models import Subject, Question


def shuffle_options(correct, wrongs):
    opts = list(wrongs[:3])
    while len(opts) < 3:
        opts.append(str(int(correct) + random.randint(1, 10)) if correct.isdigit() else correct + "?")
    pos = random.randint(0, 3)
    opts.insert(pos, correct)
    return opts[0], opts[1], opts[2], opts[3], ['A','B','C','D'][pos]


def save(subj, questions):
    added = 0
    for q in questions:
        if len(q) < 8:
            continue
        text = q[0]
        if Question.objects.filter(subject=subj, text_uz=text).exists():
            continue
        Question.objects.create(
            subject=subj,
            text_uz=q[0], option_a=q[1], option_b=q[2],
            option_c=q[3], option_d=q[4], correct_answer=q[5],
            explanation_uz=q[6], difficulty=q[7],
            is_active=True, xp_reward=10,
        )
        added += 1
    return added


def gen_math():
    qs = []
    seen = set()

    # Ko'paytma
    for _ in range(300):
        a = random.randint(2, 99)
        b = random.randint(2, 99)
        res = a * b
        text = f"{a} × {b} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+random.randint(1,15)), str(res-random.randint(1,10)), str(res+random.randint(16,30))])
        qs.append((text,a1,b1,c1,d1,ans,f"{a}×{b}={res}","easy"))

    # Bo'lish
    for _ in range(200):
        b = random.randint(2, 20)
        res = random.randint(2, 50)
        a = b * res
        text = f"{a} ÷ {b} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+1), str(res-1) if res>1 else str(res+2), str(res+3)])
        qs.append((text,a1,b1,c1,d1,ans,f"{a}÷{b}={res}","easy"))

    # Foiz
    for _ in range(200):
        base = random.choice([100,200,250,300,400,500,600,800,1000,1500,2000])
        pct  = random.choice([5,10,15,20,25,30,40,50,60,75])
        res  = int(base * pct / 100)
        text = f"{base} ning {pct}% = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+10), str(res-10) if res>10 else str(res+20), str(res+25)])
        qs.append((text,a1,b1,c1,d1,ans,f"{base}×{pct}/100={res}","easy"))

    # Kvadrat ildiz
    for n in range(1, 150):
        sq = n * n
        text = f"√{sq} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(n), [str(n+1), str(n+2), str(n-1) if n>1 else str(n+3)])
        qs.append((text,a1,b1,c1,d1,ans,f"{n}²={sq}","easy"))

    # n²
    for n in range(2, 60):
        res = n * n
        text = f"{n}² = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+n), str(res-n), str(res+2*n)])
        qs.append((text,a1,b1,c1,d1,ans,f"{n}×{n}={res}","easy"))

    # n³
    for n in range(2, 25):
        res = n ** 3
        text = f"{n}³ = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+n), str(res-n), str(res*2)])
        qs.append((text,a1,b1,c1,d1,ans,f"{n}³={res}","medium"))

    # Tenglama ax+b=c
    for _ in range(300):
        a = random.randint(2, 20)
        x = random.randint(1, 30)
        b = random.randint(1, 50)
        c = a * x + b
        text = f"{a}x + {b} = {c}, x = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(x), [str(x+1), str(x-1) if x>1 else str(x+2), str(x+2)])
        qs.append((text,a1,b1,c1,d1,ans,f"{a}x={c-b}, x={x}","medium"))

    # 2ⁿ
    for n in range(0, 20):
        res = 2 ** n
        text = f"2^{n} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res*2), str(res+1), str(res-1) if res>1 else str(res+3)])
        qs.append((text,a1,b1,c1,d1,ans,f"2^{n}={res}","easy"))

    # Log
    for base in [2, 3, 5, 10]:
        for exp in range(1, 9):
            val  = base ** exp
            text = f"log{base}({val}) = ?"
            if text in seen: continue
            seen.add(text)
            a1,b1,c1,d1,ans = shuffle_options(str(exp), [str(exp+1), str(exp-1) if exp>1 else str(exp+2), str(exp+2)])
            qs.append((text,a1,b1,c1,d1,ans,f"{base}^{exp}={val}","medium"))

    # EKUB
    for _ in range(150):
        a = random.randint(2, 100)
        b = random.randint(2, 100)
        res = gcd(a, b)
        text = f"EKUB({a}, {b}) = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+1), str(res*2), str(res+3) if res>2 else str(res+5)])
        qs.append((text,a1,b1,c1,d1,ans,f"EKUB={res}","hard"))

    # O'rtacha
    for _ in range(150):
        nums = [random.randint(1, 100) for _ in range(random.randint(3, 6))]
        res  = sum(nums) // len(nums)
        text = f"O'rtacha: {', '.join(map(str, nums))} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(res), [str(res+2), str(res-2) if res>2 else str(res+3), str(res+5)])
        qs.append((text,a1,b1,c1,d1,ans,f"Yig'indi/soni={res}","medium"))

    # Kasrlar
    for _ in range(150):
        a = random.randint(1, 10)
        b = random.randint(a+1, 20)
        c = random.randint(1, 10)
        d = random.randint(c+1, 20)
        res = Fraction(a, b) + Fraction(c, d)
        text = f"{a}/{b} + {c}/{d} = ?"
        if text in seen: continue
        seen.add(text)
        res_str = f"{res.numerator}/{res.denominator}" if res.denominator != 1 else str(res.numerator)
        a1,b1,c1,d1,ans = shuffle_options(res_str, [
            f"{res.numerator+1}/{res.denominator}",
            f"{res.numerator}/{res.denominator+1}",
            f"{a+c}/{b+d}"
        ])
        qs.append((text,a1,b1,c1,d1,ans,"Umumiy maxraj orqali","medium"))

    random.shuffle(qs)
    return qs


def gen_it():
    qs = []
    seen = set()

    # Binary → decimal
    for _ in range(300):
        n = random.randint(1, 255)
        bin_str = bin(n)[2:]
        text = f"{bin_str}₂ = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(n), [str(n+1), str(n+2), str(n-1) if n>1 else str(n+3)])
        qs.append((text,a1,b1,c1,d1,ans,"Ikkilik→O'nlik","medium"))

    # Decimal → binary
    for _ in range(200):
        n = random.randint(1, 63)
        bin_str = bin(n)[2:]
        text = f"{n}₁₀ = ?₂"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(bin_str, [
            bin(n+1)[2:], bin(n+2)[2:], bin(n-1)[2:] if n > 1 else bin(n+3)[2:]
        ])
        qs.append((text,a1,b1,c1,d1,ans,f"{n}={bin_str}₂","medium"))

    # GB → MB
    for gb in [1,2,4,8,16,32,64,128,256,512,1024]:
        mb = gb * 1024
        text = f"{gb} GB = ? MB"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(mb), [str(gb*1000), str(mb+1), str(mb//2)])
        qs.append((text,a1,b1,c1,d1,ans,"1GB=1024MB","easy"))

    # Hex → decimal
    for n in range(0, 256, 5):
        hex_str = hex(n)[2:].upper()
        text = f"0x{hex_str} = ?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(str(n), [str(n+1), str(n+8), str(n+16) if n > 0 else str(n+3)])
        qs.append((text,a1,b1,c1,d1,ans,f"16-lik=0x{hex_str}","hard"))

    random.shuffle(qs)
    return qs


def gen_physics():
    qs = []
    seen = set()

    # F = ma
    for _ in range(200):
        m = random.randint(1, 100)
        a = random.randint(1, 20)
        F = m * a
        text = f"m={m}kg, a={a}m/s², F=?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(f"{F}N", [f"{F+m}N", f"{F-a}N", f"{F*2}N"])
        qs.append((text,a1,b1,c1,d1,ans,f"F=ma={m}×{a}={F}N","easy"))

    # Ep = mgh
    for _ in range(200):
        m = random.randint(1, 50)
        h = random.randint(1, 20)
        E = m * 10 * h
        text = f"m={m}kg, h={h}m, g=10, Ep=?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(f"{E}J", [f"{E+50}J", f"{E-50}J" if E>50 else f"{E+100}J", f"{E*2}J"])
        qs.append((text,a1,b1,c1,d1,ans,f"Ep=mgh={m}×10×{h}={E}J","medium"))

    # Ek = mv²/2
    for _ in range(200):
        m = random.randint(1, 20)
        v = random.randint(2, 20)
        E = m * v * v // 2
        text = f"m={m}kg, v={v}m/s, Ek=?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(f"{E}J", [f"{E+10}J", f"{E-5}J" if E>5 else f"{E+20}J", f"{E*2}J"])
        qs.append((text,a1,b1,c1,d1,ans,f"Ek=mv²/2={m}×{v}²/2={E}J","medium"))

    # I = U/R
    for _ in range(200):
        U = random.choice([6,12,24,36,48,60,110,220])
        R = random.randint(2, 100)
        I = round(U / R, 2)
        text = f"U={U}V, R={R}Ω, I=?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(f"{I}A", [f"{round(I*2,2)}A", f"{round(I+1,2)}A", f"{round(I+0.5,2)}A"])
        qs.append((text,a1,b1,c1,d1,ans,f"I=U/R={U}/{R}={I}A","easy"))

    # P = UI
    for _ in range(150):
        U = random.choice([12,24,110,220])
        I = random.randint(1, 20)
        P = U * I
        text = f"U={U}V, I={I}A, P=?"
        if text in seen: continue
        seen.add(text)
        a1,b1,c1,d1,ans = shuffle_options(f"{P}W", [f"{P+U}W", f"{P-I}W" if P>I else f"{P+10}W", f"{P*2}W"])
        qs.append((text,a1,b1,c1,d1,ans,f"P=UI={U}×{I}={P}W","medium"))

    random.shuffle(qs)
    return qs


# ── SAQLASH ──────────────────────────────────────────
print("="*50)
print("  Savollar generatsiya qilinmoqda...")
print("="*50)

tasks = [
    ('math',    gen_math),
    ('it',      gen_it),
    ('physics', gen_physics),
]

total = 0
for code, func in tasks:
    try:
        subj = Subject.objects.get(code=code)
    except Subject.DoesNotExist:
        print(f"  ⚠️ '{code}' topilmadi")
        continue
    before = Question.objects.filter(subject=subj, is_active=True).count()
    print(f"\n📚 {subj.name_uz} (mavjud: {before} ta)...")
    qs = func()
    added = save(subj, qs)
    after  = Question.objects.filter(subject=subj, is_active=True).count()
    print(f"  ✅ +{added} yangi → jami {after} ta savol")
    total += added

print(f"\n{'='*50}")
print(f"✅ Jami {total} ta yangi savol!")
print(f"{'='*50}")