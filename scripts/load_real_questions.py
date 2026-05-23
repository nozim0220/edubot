"""Haqiqiy savollarni DB ga yuklash."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ.setdefault('USE_SQLITE', 'true')
django.setup()

from apps.education.models import Subject, Question
from apps.mock_web.real_questions import (
    IELTS_READING_PASSAGES, IELTS_LISTENING_SECTIONS,
    SAT_MATH_QUESTIONS, DTM_QUESTIONS
)

total = 0

# ── IELTS READING ────────────────────────────────────
print("\n📖 IELTS Reading savollar...")
try:
    ielts_subj = Subject.objects.get(code='ielts')
    for passage in IELTS_READING_PASSAGES:
        passage_info = f"[{passage['title']}] "
        for q in passage['questions']:
            if q['type'] == 'tfng':
                text = passage_info + q['text'] + " (TRUE/FALSE/NOT GIVEN)"
                opts = ['TRUE', 'FALSE', 'NOT GIVEN', 'Cannot Say']
                ans  = {'TRUE':'A','FALSE':'B','NOT GIVEN':'C'}[q['answer']]
            elif q['type'] == 'mcq':
                text = passage_info + q['text']
                opts = [o.split(') ',1)[1] if ') ' in o else o for o in q['options']]
                ans  = q['answer']
            else:  # fill
                text = passage_info + q['text'] + " [fill in]"
                ans_word = q['answer']
                opts = [ans_word, ans_word+"s", "the "+ans_word, ans_word.lower()+"ed"]
                ans  = 'A'

            if not Question.objects.filter(subject=ielts_subj, text_uz=text).exists():
                Question.objects.create(
                    subject=ielts_subj,
                    text_uz=text,
                    option_a=opts[0], option_b=opts[1] if len(opts)>1 else '',
                    option_c=opts[2] if len(opts)>2 else '', option_d=opts[3] if len(opts)>3 else '',
                    correct_answer=ans,
                    explanation_uz=q.get('explanation',''),
                    difficulty='medium', is_active=True, xp_reward=15,
                )
                total += 1
    count = Question.objects.filter(subject=ielts_subj, is_active=True).count()
    print(f"  ✅ IELTS: jami {count} ta savol")
except Subject.DoesNotExist:
    print("  ⚠️ IELTS subject topilmadi")

# ── IELTS LISTENING ───────────────────────────────────
print("\n🎧 IELTS Listening savollar...")
try:
    ielts_subj = Subject.objects.get(code='ielts')
    for section in IELTS_LISTENING_SECTIONS:
        sec_info = f"[Section {section['section']}: {section['title']}] "
        for q in section['questions']:
            if q['type'] == 'fill':
                text = sec_info + q['text'] + " [listening]"
                ans_word = q['answer']
                opts = [ans_word, ans_word+"s", "the "+ans_word, ans_word.upper()]
                ans  = 'A'
            else:  # mcq
                text = sec_info + q['text']
                opts = [o.split(') ',1)[1] if ') ' in o else o for o in q['options']]
                ans  = q['answer']

            if not Question.objects.filter(subject=ielts_subj, text_uz=text).exists():
                Question.objects.create(
                    subject=ielts_subj,
                    text_uz=text,
                    option_a=opts[0], option_b=opts[1] if len(opts)>1 else '',
                    option_c=opts[2] if len(opts)>2 else '', option_d=opts[3] if len(opts)>3 else '',
                    correct_answer=ans,
                    explanation_uz=q.get('explanation',''),
                    difficulty='medium', is_active=True, xp_reward=15,
                )
                total += 1
    print(f"  ✅ IELTS Listening: qo'shildi")
except Subject.DoesNotExist:
    print("  ⚠️ topilmadi")

# ── SAT MATH ──────────────────────────────────────────
print("\n🔢 SAT Math savollar...")
try:
    sat_subj = Subject.objects.get(code='sat')
    for q in SAT_MATH_QUESTIONS:
        text, a, b, c, d, ans, exp, diff = q
        if not Question.objects.filter(subject=sat_subj, text_uz=text).exists():
            Question.objects.create(
                subject=sat_subj,
                text_uz=text, option_a=a, option_b=b, option_c=c, option_d=d,
                correct_answer=ans, explanation_uz=exp,
                difficulty=diff, is_active=True, xp_reward=15,
            )
            total += 1
    count = Question.objects.filter(subject=sat_subj, is_active=True).count()
    print(f"  ✅ SAT Math: jami {count} ta savol")
except Subject.DoesNotExist:
    print("  ⚠️ SAT subject topilmadi")

# ── DTM ───────────────────────────────────────────────
print("\n📊 DTM fanlar...")
dtm_map = {
    'math':      'math',
    'physics':   'physics',
    'chemistry': 'chemistry',
    'biology':   'biology',
    'history':   'history',
    'english':   'english',
}

for dtm_key, subj_code in dtm_map.items():
    try:
        subj = Subject.objects.get(code=subj_code)
        qs   = DTM_QUESTIONS.get(dtm_key, [])
        added = 0
        for q in qs:
            if len(q) < 8: continue
            text, a, b, c, d, ans, exp, diff, *_ = q
            if not Question.objects.filter(subject=subj, text_uz=text).exists():
                Question.objects.create(
                    subject=subj,
                    text_uz=text, option_a=a, option_b=b, option_c=c, option_d=d,
                    correct_answer=ans, explanation_uz=exp,
                    difficulty=diff, is_active=True, xp_reward=15,
                )
                added += 1
                total += 1
        count = Question.objects.filter(subject=subj, is_active=True).count()
        print(f"  ✅ {subj.name_uz}: +{added} → jami {count} ta")
    except Subject.DoesNotExist:
        print(f"  ⚠️ '{subj_code}' topilmadi")

print(f"\n{'='*50}")
print(f"✅ Jami {total} ta haqiqiy savol qo'shildi!")
print(f"{'='*50}")