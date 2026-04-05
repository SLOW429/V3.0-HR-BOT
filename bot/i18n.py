import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LANG_SETTINGS_PATH = DATA_DIR / 'lang_settings.json'

SUPPORTED_LANGUAGES = {
    'ar': 'العربية',
    'en': 'English',
    'tr': 'Türkçe',
    'fr': 'Français',
    'ru': 'Русский',
    'es': 'Español',
    'fa': 'فارسی',
    'tl': 'Filipino',
    'it': 'Italiano',
    'nl': 'Nederlands',
}

LANGUAGE_ALIASES = {
    'arabic': 'ar', 'ar': 'ar', 'عربي': 'ar', 'العربية': 'ar',
    'english': 'en', 'en': 'en', 'انجليزي': 'en', 'englishus': 'en',
    'turkish': 'tr', 'tr': 'tr', 'تركي': 'tr', 'türkçe': 'tr',
    'french': 'fr', 'fr': 'fr', 'فرنسي': 'fr', 'francais': 'fr', 'français': 'fr',
    'russian': 'ru', 'ru': 'ru', 'روسي': 'ru',
    'spanish': 'es', 'es': 'es', 'اسباني': 'es', 'español': 'es',
    'persian': 'fa', 'farsi': 'fa', 'fa': 'fa', 'فارسي': 'fa', 'فارسی': 'fa',
    'filipino': 'tl', 'tagalog': 'tl', 'tl': 'tl', 'فلبيني': 'tl',
    'italian': 'it', 'it': 'it', 'ايطالي': 'it',
    'dutch': 'nl', 'netherlands': 'nl', 'nederlands': 'nl', 'nl': 'nl', 'هولندي': 'nl', 'نزرلاندي': 'nl',
}

BASE_EN = {
    'permission_denied': 'You are not allowed to do that.',
    'dj_add_usage': 'Use: dj add @user',
    'dj_del_usage': 'Use: dj del @user',
    'dj_added': 'New DJ added',
    'dj_removed': 'DJ removed',
    'dj_list_title': 'DJ LIST',
    'none': 'None',
    'your_points': 'Your balance: {points} points',
    'daily_ready_in': 'Daily reward available in {hours}h and {minutes}m',
    'daily_claimed': 'You received {points} daily points',
    'your_points_now': 'Your balance is now: {points}',
    'shop_title': 'RADIO SHOP',
    'shop_dj_item': 'DJ for {days} days = {price} points',
    'buy_dj_success': 'DJ purchased for {days} days',
    'points_not_enough': 'Not enough points. Price: {price} | Your balance: {points}',
    'no_roles': 'You do not have any active roles.',
    'your_roles': 'YOUR ROLES',
    'days_left': '{days} days',
    'top_points': 'TOP POINTS',
    'no_leaderboard': 'No leaderboard yet.',
    'dj_required': 'Only DJ can use this command.',
    'play_usage': 'Write a song name after -play',
    'track_added': 'Track added to queue',
    'by_user': 'By: {user}',
    'queue_title': 'QUEUE',
    'queue_empty': 'Queue is empty.',
    'removed_track': 'Removed: {title}',
    'queue_invalid_number': 'Enter a valid queue number.',
    'queue_move_ok': 'Queue order updated.',
    'queue_move_usage': 'Correct usage: -move 3 1',
    'nothing_playing': 'Nothing is playing right now.',
    'now_playing': 'NOW PLAYING',
    'current_track': 'Current',
    'up_next': 'Next',
    'library_empty': 'Library is empty.',
    'library_title': 'LIBRARY',
    'history_empty': 'No play history yet.',
    'history_title': 'RECENT TRACKS',
    'queue_cleared': 'Queue cleared',
    'playback_stopped': 'Current playback has been stopped',
    'skip_done': 'Current song skipped',
    'stop_sent': 'Stop command sent',
    'stop_wait': 'The current song will stop shortly',
    'song_link_missing': 'No current song link.',
    'language_changed': 'Bot language changed to: {language}',
    'language_invalid': 'Unsupported language. Available: {languages}',
    'current_language': 'Current bot language: {language}',
    'language_title': 'AVAILABLE LANGUAGES',
    'language_usage': 'Use: lang <code>',
    'command_error': 'An error occurred: {error}',
}

TRANSLATIONS = {
    'en': BASE_EN,
    'ar': {
        **BASE_EN,
        'permission_denied': 'غير مسموح لك.',
        'dj_add_usage': 'اكتب: dj add @user',
        'dj_del_usage': 'اكتب: dj del @user',
        'dj_added': 'تمت إضافة DJ جديد',
        'dj_removed': 'تم حذف DJ',
        'dj_list_title': 'قائمة الـ DJ',
        'none': 'لا يوجد',
        'your_points': 'رصيدك: {points} نقطة',
        'daily_ready_in': 'اليومي جاهز بعد {hours} ساعة و {minutes} دقيقة',
        'daily_claimed': 'أخذت {points} نقطة يومية',
        'your_points_now': 'رصيدك الآن: {points}',
        'shop_title': 'متجر الراديو',
        'shop_dj_item': 'DJ لمدة {days} أيام = {price} نقطة',
        'buy_dj_success': 'تم شراء DJ لمدة {days} أيام',
        'points_not_enough': 'نقاطك غير كافية. السعر: {price} | رصيدك: {points}',
        'no_roles': 'لا تملك أي رتب حالياً',
        'your_roles': 'رتبك',
        'days_left': '{days} يوم',
        'top_points': 'أفضل النقاط',
        'no_leaderboard': 'لا يوجد ترتيب بعد',
        'dj_required': 'الأمر ده للـ DJ فقط.',
        'play_usage': 'اكتب اسم الأغنية بعد -play',
        'track_added': 'تمت إضافة الأغنية للقائمة',
        'by_user': 'بواسطة: {user}',
        'queue_title': 'الكيو',
        'queue_empty': 'لا توجد طلبات',
        'removed_track': 'تم حذف: {title}',
        'queue_invalid_number': 'اكتب رقم صحيح من الكيو',
        'queue_move_ok': 'تم تعديل ترتيب الكيو',
        'queue_move_usage': 'استخدام صحيح: -move 3 1',
        'nothing_playing': 'لا يوجد تشغيل حالي',
        'now_playing': 'يعمل الآن',
        'current_track': 'الحالية',
        'up_next': 'التالية',
        'library_empty': 'المكتبة فارغة',
        'library_title': 'المكتبة',
        'history_empty': 'لا يوجد تاريخ تشغيل بعد',
        'history_title': 'آخر المقاطع',
        'queue_cleared': 'تم مسح القائمة',
        'playback_stopped': 'وتم إيقاف التشغيل الحالي',
        'skip_done': 'تم تخطي الأغنية الحالية',
        'stop_sent': 'تم إرسال أمر الإيقاف',
        'stop_wait': 'سيتم إيقاف الأغنية الحالية',
        'song_link_missing': 'لا يوجد رابط حالي',
        'language_changed': 'تم تغيير لغة البوت إلى: {language}',
        'language_invalid': 'اللغة غير مدعومة. المتاح: {languages}',
        'current_language': 'لغة البوت الحالية: {language}',
        'language_title': 'اللغات المتاحة',
        'language_usage': 'اكتب: lang <اللغة>',
        'command_error': 'حصل خطأ: {error}',
    },
    'tr': {**BASE_EN, 'permission_denied': 'Bunu yapma iznin yok.', 'dj_add_usage': 'Kullanım: dj add @user', 'dj_del_usage': 'Kullanım: dj del @user', 'dj_added': 'Yeni DJ eklendi', 'dj_removed': 'DJ kaldırıldı', 'dj_list_title': 'DJ LİSTESİ', 'none': 'Yok', 'your_points': 'Bakiyen: {points} puan', 'daily_ready_in': 'Günlük ödül {hours} saat {minutes} dakika sonra hazır', 'daily_claimed': '{points} günlük puan aldın', 'your_points_now': 'Yeni bakiyen: {points}', 'shop_title': 'RADYO MAĞAZASI', 'shop_dj_item': '{days} gün DJ = {price} puan', 'buy_dj_success': '{days} günlüğüne DJ satın alındı', 'points_not_enough': 'Yetersiz puan. Fiyat: {price} | Bakiyen: {points}', 'no_roles': 'Aktif rolün yok.', 'your_roles': 'ROLLERİN', 'days_left': '{days} gün', 'top_points': 'EN YÜKSEK PUANLAR', 'no_leaderboard': 'Henüz sıralama yok.', 'dj_required': 'Bu komut sadece DJ içindir.', 'play_usage': '-play komutundan sonra şarkı adı yaz', 'track_added': 'Parça kuyruğa eklendi', 'by_user': 'Ekleyen: {user}', 'queue_title': 'KUYRUK', 'queue_empty': 'Kuyruk boş.', 'removed_track': 'Kaldırıldı: {title}', 'queue_invalid_number': 'Geçerli bir sıra numarası gir.', 'queue_move_ok': 'Kuyruk sırası güncellendi.', 'queue_move_usage': 'Doğru kullanım: -move 3 1', 'nothing_playing': 'Şu anda çalan bir şey yok.', 'now_playing': 'ŞİMDİ ÇALIYOR', 'current_track': 'Geçerli', 'up_next': 'Sıradaki', 'library_empty': 'Kütüphane boş.', 'library_title': 'KÜTÜPHANE', 'history_empty': 'Henüz oynatma geçmişi yok.', 'history_title': 'SON PARÇALAR', 'queue_cleared': 'Kuyruk temizlendi', 'playback_stopped': 'Geçerli çalma durduruldu', 'skip_done': 'Geçerli şarkı atlandı', 'stop_sent': 'Durdurma komutu gönderildi', 'stop_wait': 'Geçerli şarkı birazdan duracak', 'song_link_missing': 'Geçerli şarkı bağlantısı yok.', 'language_changed': 'Bot dili değiştirildi: {language}', 'language_invalid': 'Desteklenmeyen dil. Mevcut: {languages}', 'current_language': 'Geçerli bot dili: {language}', 'language_title': 'MEVCUT DİLLER', 'language_usage': 'Kullanım: lang <dil>', 'command_error': 'Bir hata oluştu: {error}'},
    'fr': {**BASE_EN, 'permission_denied': 'Tu n’as pas la permission.', 'your_points': 'Ton solde : {points} points', 'daily_claimed': 'Tu as reçu {points} points quotidiens', 'language_changed': 'Langue du bot modifiée en : {language}', 'language_invalid': 'Langue non prise en charge. Disponibles : {languages}', 'current_language': 'Langue actuelle du bot : {language}', 'language_title': 'LANGUES DISPONIBLES'},
    'ru': {**BASE_EN, 'permission_denied': 'У тебя нет доступа к этой команде.', 'your_points': 'Твой баланс: {points} очков', 'daily_claimed': 'Ты получил {points} ежедневных очков', 'language_changed': 'Язык бота изменён на: {language}', 'language_invalid': 'Язык не поддерживается. Доступно: {languages}', 'current_language': 'Текущий язык бота: {language}', 'language_title': 'ДОСТУПНЫЕ ЯЗЫКИ'},
    'es': {**BASE_EN, 'permission_denied': 'No tienes permiso para eso.', 'your_points': 'Tu saldo: {points} puntos', 'daily_claimed': 'Recibiste {points} puntos diarios', 'language_changed': 'Idioma del bot cambiado a: {language}', 'language_invalid': 'Idioma no compatible. Disponibles: {languages}', 'current_language': 'Idioma actual del bot: {language}', 'language_title': 'IDIOMAS DISPONIBLES'},
    'fa': {**BASE_EN, 'permission_denied': 'شما اجازه این کار را ندارید.', 'your_points': 'موجودی شما: {points} امتیاز', 'daily_claimed': 'شما {points} امتیاز روزانه گرفتید', 'language_changed': 'زبان ربات تغییر کرد به: {language}', 'language_invalid': 'این زبان پشتیبانی نمی‌شود. موجود: {languages}', 'current_language': 'زبان فعلی ربات: {language}', 'language_title': 'زبان‌های موجود'},
    'tl': {**BASE_EN, 'permission_denied': 'Wala kang pahintulot para diyan.', 'your_points': 'Balanse mo: {points} puntos', 'daily_claimed': 'Nakatanggap ka ng {points} daily points', 'language_changed': 'Napalitan ang wika ng bot sa: {language}', 'language_invalid': 'Hindi suportadong wika. Available: {languages}', 'current_language': 'Kasalukuyang wika ng bot: {language}', 'language_title': 'MGA AVAILABLE NA WIKA'},
    'it': {**BASE_EN, 'permission_denied': 'Non hai il permesso.', 'your_points': 'Il tuo saldo: {points} punti', 'daily_claimed': 'Hai ricevuto {points} punti giornalieri', 'language_changed': 'Lingua del bot cambiata in: {language}', 'language_invalid': 'Lingua non supportata. Disponibili: {languages}', 'current_language': 'Lingua attuale del bot: {language}', 'language_title': 'LINGUE DISPONIBILI'},
    'nl': {**BASE_EN, 'permission_denied': 'Je hebt daar geen toestemming voor.', 'your_points': 'Je saldo: {points} punten', 'daily_claimed': 'Je hebt {points} dagelijkse punten ontvangen', 'language_changed': 'Bottaal gewijzigd naar: {language}', 'language_invalid': 'Niet-ondersteunde taal. Beschikbaar: {languages}', 'current_language': 'Huidige bottaal: {language}', 'language_title': 'BESCHIKBARE TALEN'},
}


def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def normalize_language_code(raw: str | None) -> str | None:
    if not raw:
        return None
    key = ''.join(ch for ch in str(raw).strip().lower() if ch.isalnum() or ch in {'_', '-'})
    return LANGUAGE_ALIASES.get(key, key if key in SUPPORTED_LANGUAGES else None)


def get_language() -> str:
    data = load_json(LANG_SETTINGS_PATH, {'language': 'ar'})
    lang = normalize_language_code(data.get('language')) or 'ar'
    return lang if lang in SUPPORTED_LANGUAGES else 'ar'


def set_language(lang: str) -> bool:
    normalized = normalize_language_code(lang)
    if normalized not in SUPPORTED_LANGUAGES:
        return False
    save_json(LANG_SETTINGS_PATH, {'language': normalized})
    return True


def tr(key: str, lang: str | None = None, **kwargs) -> str:
    chosen = lang or get_language()
    bundle = TRANSLATIONS.get(chosen, TRANSLATIONS['en'])
    text = bundle.get(key, TRANSLATIONS['en'].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def available_languages_text() -> str:
    return ', '.join(f'{code}={name}' for code, name in SUPPORTED_LANGUAGES.items())
