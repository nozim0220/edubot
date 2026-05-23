"""Internationalization texts."""

TEXTS = {
    'uz': {
        'welcome': (
            "🎓 <b>EduBot'ga xush kelibsiz!</b>\n\n"
            "📚 O'qish, test ishlash va eng yaxshi universitetlarni topishga yordam beraman!\n\n"
            "🚀 Boshlash uchun quyidagi tugmalardan birini tanlang:"
        ),
        'welcome_back': "👋 Qaytib keldingiz, <b>{name}</b>!\n\n📊 XP: {xp} | 🏆 Daraja: {level}",
        'must_subscribe': (
            "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!</b>\n\n"
            "✅ Obuna bo'lgach \"Tekshirish\" tugmasini bosing."
        ),
        'subscribed': "✅ Ajoyib! Endi botdan to'liq foydalanishingiz mumkin!",
        'not_subscribed': "❌ Siz hali barcha kanallarga obuna bo'lmagansiz. Iltimos, tekshiring.",
        'profile_title': "👤 <b>Mening profilim</b>",
        'education_menu': "📚 <b>Ta'lim bo'limi</b>\n\nQaysi yo'nalishni tanlaysiz?",
        'select_subject': "📖 <b>Fan tanlang:</b>",
        'quiz_start': "🎯 <b>Test boshlandi!</b>\n\n{title}\n\n⏱ Vaqt: {time}",
        'question_text': "❓ <b>Savol {num}/{total}</b>\n\n{text}",
        'correct': "✅ <b>To'g'ri!</b> +{xp} XP",
        'wrong': "❌ <b>Noto'g'ri!</b>\nTo'g'ri javob: <b>{answer}</b>",
        'test_complete': (
            "🏁 <b>Test yakunlandi!</b>\n\n"
            "📊 Natija: {correct}/{total} ({score}%)\n"
            "⭐ Daraja: {passed}\n"
            "🎁 XP qazonildi: +{xp}"
        ),
        'ai_menu': "🤖 <b>AI Yordamchi</b>\n\nNima haqida yordam kerak?",
        'ai_waiting': "🤔 O'ylayapman...",
        'ai_limit': "⚠️ Kunlik limit tugadi ({limit} ta so'rov).\n💎 Premium olish uchun: /premium",
        'university_menu': "🏫 <b>Universitetlar bazasi</b>",
        'premium_menu': "💎 <b>Premium obuna</b>\n\nPremium imkoniyatlar:",
        'settings_menu': "⚙️ <b>Sozlamalar</b>",
        'language_changed': "✅ Til o'zgartirildi!",
        'back': "🔙 Orqaga",
        'main_menu': "🏠 Asosiy menyu",
        'daily_challenge': "🔥 <b>Kunlik vazifa</b>",
        'leaderboard': "🏆 <b>Reyting</b>",
        'no_daily': "📅 Bugun uchun kunlik vazifa yo'q. Ertaga keling!",
    },
    'ru': {
        'welcome': (
            "🎓 <b>Добро пожаловать в EduBot!</b>\n\n"
            "📚 Помогу учиться, проходить тесты и найти лучшие университеты!\n\n"
            "🚀 Выберите одну из кнопок ниже:"
        ),
        'welcome_back': "👋 С возвращением, <b>{name}</b>!\n\n📊 XP: {xp} | 🏆 Уровень: {level}",
        'must_subscribe': (
            "🔒 <b>Для использования бота подпишитесь на каналы!</b>\n\n"
            "✅ После подписки нажмите «Проверить»."
        ),
        'subscribed': "✅ Отлично! Теперь вы можете пользоваться ботом!",
        'not_subscribed': "❌ Вы ещё не подписались на все каналы.",
        'profile_title': "👤 <b>Мой профиль</b>",
        'education_menu': "📚 <b>Раздел обучения</b>\n\nЧто выберете?",
        'select_subject': "📖 <b>Выберите предмет:</b>",
        'quiz_start': "🎯 <b>Тест начался!</b>\n\n{title}\n\n⏱ Время: {time}",
        'question_text': "❓ <b>Вопрос {num}/{total}</b>\n\n{text}",
        'correct': "✅ <b>Правильно!</b> +{xp} XP",
        'wrong': "❌ <b>Неправильно!</b>\nПравильный ответ: <b>{answer}</b>",
        'test_complete': (
            "🏁 <b>Тест завершён!</b>\n\n"
            "📊 Результат: {correct}/{total} ({score}%)\n"
            "⭐ Статус: {passed}\n"
            "🎁 Получено XP: +{xp}"
        ),
        'ai_menu': "🤖 <b>ИИ Помощник</b>\n\nВ чём нужна помощь?",
        'ai_waiting': "🤔 Думаю...",
        'ai_limit': "⚠️ Дневной лимит исчерпан ({limit} запросов).\n💎 Купить Premium: /premium",
        'university_menu': "🏫 <b>База университетов</b>",
        'premium_menu': "💎 <b>Premium подписка</b>\n\nВозможности Premium:",
        'settings_menu': "⚙️ <b>Настройки</b>",
        'language_changed': "✅ Язык изменён!",
        'back': "🔙 Назад",
        'main_menu': "🏠 Главное меню",
        'daily_challenge': "🔥 <b>Ежедневное задание</b>",
        'leaderboard': "🏆 <b>Рейтинг</b>",
        'no_daily': "📅 Сегодня нет задания. Приходите завтра!",
    },
    'en': {
        'welcome': (
            "🎓 <b>Welcome to EduBot!</b>\n\n"
            "📚 I'll help you study, take tests, and find the best universities!\n\n"
            "🚀 Choose one of the options below:"
        ),
        'welcome_back': "👋 Welcome back, <b>{name}</b>!\n\n📊 XP: {xp} | 🏆 Level: {level}",
        'must_subscribe': (
            "🔒 <b>Please subscribe to the required channels to use the bot!</b>\n\n"
            "✅ After subscribing, press «Check»."
        ),
        'subscribed': "✅ Great! You can now use the bot fully!",
        'not_subscribed': "❌ You haven't subscribed to all channels yet.",
        'profile_title': "👤 <b>My Profile</b>",
        'education_menu': "📚 <b>Education</b>\n\nWhat would you like to do?",
        'select_subject': "📖 <b>Select subject:</b>",
        'quiz_start': "🎯 <b>Test started!</b>\n\n{title}\n\n⏱ Time: {time}",
        'question_text': "❓ <b>Question {num}/{total}</b>\n\n{text}",
        'correct': "✅ <b>Correct!</b> +{xp} XP",
        'wrong': "❌ <b>Wrong!</b>\nCorrect answer: <b>{answer}</b>",
        'test_complete': (
            "🏁 <b>Test completed!</b>\n\n"
            "📊 Score: {correct}/{total} ({score}%)\n"
            "⭐ Status: {passed}\n"
            "🎁 XP earned: +{xp}"
        ),
        'ai_menu': "🤖 <b>AI Assistant</b>\n\nWhat do you need help with?",
        'ai_waiting': "🤔 Thinking...",
        'ai_limit': "⚠️ Daily limit reached ({limit} requests).\n💎 Get Premium: /premium",
        'university_menu': "🏫 <b>University Database</b>",
        'premium_menu': "💎 <b>Premium Subscription</b>\n\nPremium features:",
        'settings_menu': "⚙️ <b>Settings</b>",
        'language_changed': "✅ Language changed!",
        'back': "🔙 Back",
        'main_menu': "🏠 Main Menu",
        'daily_challenge': "🔥 <b>Daily Challenge</b>",
        'leaderboard': "🏆 <b>Leaderboard</b>",
        'no_daily': "📅 No daily challenge today. Come back tomorrow!",
    },
}


def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS['uz']).get(key, TEXTS['uz'].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
