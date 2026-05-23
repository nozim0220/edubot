"""Mock natijasiga qarab universitet tavsiyasi."""
from typing import List


# IELTS band → taxminiy ballar
IELTS_MAP = {
    9.0: 100, 8.5: 95, 8.0: 90, 7.5: 85, 7.0: 78,
    6.5: 70,  6.0: 62, 5.5: 54, 5.0: 45, 4.5: 36,
    4.0: 27,  3.5: 18,
}

# SAT → foiz
SAT_MAP = {
    1600: 100, 1550: 97, 1500: 94, 1450: 90, 1400: 85,
    1350: 80,  1300: 74, 1250: 68, 1200: 61, 1150: 54,
    1100: 47,  1050: 40, 1000: 33,
}


def score_to_ielts(score: int) -> float:
    """Mock natijasidan IELTS band taxmin."""
    band = round(score / 100 * 9, 1)
    return min(9.0, max(1.0, band))


def score_to_sat(score: int) -> int:
    """Mock natijasidan SAT taxmin."""
    sat = 400 + round((score / 100) * 1200)
    return min(1600, max(400, sat))


def recommend_universities_by_score(
    score: int,
    exam_type: str,
    user=None,
) -> List[dict]:
    """Mock bali asosida universitet tavsiyalari."""
    try:
        from apps.universities.models import University

        results = []
        unis = list(
            University.objects.filter(is_active=True)
            .order_by('world_ranking', 'national_ranking')[:50]
        )

        for u in unis:
            chance = _calc_match(score, exam_type, u)
            if chance >= 20:
                results.append({
                    'university': u,
                    'chance': chance,
                    'flag': _flag(u.country),
                })

        results.sort(key=lambda x: x['chance'], reverse=True)

        # Yuqori (>70%), o'rta (40-70%), past (20-40%) kategoriyalarga ajrat
        top    = [r for r in results if r['chance'] >= 70][:3]
        middle = [r for r in results if 40 <= r['chance'] < 70][:4]
        reach  = [r for r in results if 20 <= r['chance'] < 40][:3]

        return top + middle + reach
    except Exception:
        return []


def _calc_match(score: int, exam_type: str, u) -> int:
    """Bir university uchun mos kelish foizi."""
    if exam_type == 'ielts':
        user_band = score_to_ielts(score)
        if u.required_ielts:
            req = float(u.required_ielts)
            ratio = user_band / req
            return min(97, max(0, int(ratio * 75)))
        if u.country == 'UZ':
            return max(0, min(80, score - 10))

    elif exam_type == 'sat':
        user_sat = score_to_sat(score)
        if u.required_sat:
            ratio = user_sat / u.required_sat
            return min(97, max(0, int(ratio * 80)))

    elif exam_type in ('math', 'physics', 'chemistry', 'biology', 'history', 'it'):
        # DTM ball taxmin: 30 ta savoldan
        dtm_estimate = round((score / 100) * 30)
        if u.dtm_passing_score:
            ratio = dtm_estimate / u.dtm_passing_score * 30
            return min(95, max(0, int(ratio * 70)))
        if u.country == 'UZ':
            return max(20, min(90, score - 5))

    return 0


def _flag(code: str) -> str:
    flags = {
        'UZ':'🇺🇿','US':'🇺🇸','GB':'🇬🇧','DE':'🇩🇪',
        'RU':'🇷🇺','KR':'🇰🇷','TR':'🇹🇷','CN':'🇨🇳',
        'JP':'🇯🇵','MY':'🇲🇾',
    }
    return flags.get(code, '🌍')
