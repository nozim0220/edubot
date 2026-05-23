"""AI Assistant services."""
import logging
from datetime import date
from django.conf import settings

logger = logging.getLogger('bot')

SYSTEM_PROMPTS = {
    'homework':   "Sen O'zbekiston o'quvchilariga yordam beradigan aqlli o'qituvchisan. Uy ishlarini bosqichma-bosqich tushuntir. O'zbek tilida javob ber.",
    'math':       "Sen matematika bo'yicha ekspert. Masalani bosqichma-bosqich yech.",
    'explain':    "Sen murakkab mavzularni oddiy tushuntiradigan o'qituvchisan.",
    'grammar':    "Sen ingliz tili grammatikasi eksperti. Xatolarni to'g'irla.",
    'essay':      "Sen esse yozishga yordam beradigan murabbiy.",
    'career':     "Sen karyera va universitet tanlash bo'yicha maslahatchi.",
    'study_plan': "Sen shaxsiy o'qish rejasi tuzib berasan.",
    'general':    "Sen ABT Yordamchi AI assistantisan. O'zbek tilida javob ber.",
}


def get_ai_client():
    import httpx
    groq_key = getattr(settings, 'GROQ_API_KEY', '').strip()
    if groq_key and len(groq_key) > 10 and not groq_key.startswith('your'):
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1",
                http_client=httpx.Client(),
            )
            model = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
            return client, model
        except Exception as e:
            logger.error(f"Groq xato: {e}")

    oai_key = getattr(settings, 'OPENAI_API_KEY', '').strip()
    if oai_key and oai_key.startswith('sk-') and 'fake' not in oai_key.lower():
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=oai_key,
                http_client=httpx.Client(),
            )
            model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o')
            return client, model
        except Exception as e:
            logger.error(f"OpenAI xato: {e}")

    logger.warning("AI client topilmadi!")
    return None, None


get_client = get_ai_client


def check_limit(user):
    from apps.ai_assistant.models import AIUsageLog
    today  = date.today()
    log, _ = AIUsageLog.objects.get_or_create(user=user, date=today)
    limit  = getattr(settings, 'AI_DAILY_FREE_LIMIT', 100)
    return max(0, limit - log.requests_count), limit, log


class AIService:

    def get_usage_stats(self, user):
        remaining, limit, log = check_limit(user)
        return {
            'used_today': log.requests_count,
            'limit':      limit,
            'remaining':  remaining,
        }

    def get_or_create_chat(self, user, chat_type='general'):
        from apps.ai_assistant.models import AIChat
        # get_or_create o'rniga filter — takroriy xatolikdan qochish
        chat = AIChat.objects.filter(
            user=user, chat_type=chat_type, is_saved=False
        ).order_by('-updated_at').first()
        if not chat:
            chat = AIChat.objects.create(
                user=user, chat_type=chat_type,
                is_saved=False, title=chat_type
            )
        return chat

    def send_message(self, user, chat, user_message: str) -> dict:
        from apps.ai_assistant.models import AIMessage, AIUsageLog

        remaining, limit, log = check_limit(user)
        if remaining <= 0:
            raise Exception(
                f"limit_exceeded: Kunlik limit tugadi ({limit} ta). Ertaga davom eting."
            )

        client, model = get_ai_client()
        if not client:
            raise Exception(
                "sozlanmagan: AI sozlanmagan!\n\n"
                "Groq (bepul) API key oling:\n"
                "👉 https://console.groq.com\n\n"
                ".env faylida:\nGROQ_API_KEY=gsk_..."
            )

        AIMessage.objects.create(chat=chat, role='user', content=user_message)

        history = list(
            AIMessage.objects.filter(chat=chat).order_by('-created_at')[:10]
        )
        history.reverse()

        messages = [
            {'role': 'system',
             'content': SYSTEM_PROMPTS.get(chat.chat_type, SYSTEM_PROMPTS['general'])}
        ]
        for m in history:
            if m.role in ('user', 'assistant'):
                messages.append({'role': m.role, 'content': m.content})

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 2000),
                temperature=0.7,
            )
            ai_text     = resp.choices[0].message.content
            tokens_used = getattr(resp.usage, 'total_tokens', 0)
        except Exception as e:
            err = str(e)
            logger.error(f"AI API xato: {err}")
            if 'api_key' in err.lower() or 'auth' in err.lower() or '401' in err:
                raise Exception("api_key_xato: API key noto'g'ri!")
            if 'rate' in err.lower() or '429' in err:
                raise Exception("rate_limit: Biroz kuting.")
            raise Exception(f"AI xato: {err[:200]}")

        AIMessage.objects.create(
            chat=chat, role='assistant',
            content=ai_text, tokens_used=tokens_used
        )
        chat.total_tokens += tokens_used
        chat.save(update_fields=['total_tokens', 'updated_at'])

        log.requests_count += 1
        log.tokens_used    += tokens_used
        log.save(update_fields=['requests_count', 'tokens_used'])

        return {
            'response':           ai_text,
            'remaining_requests': remaining - 1,
            'tokens_used':        tokens_used,
        }