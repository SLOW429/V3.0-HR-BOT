import json
import os
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LANG_SETTINGS_PATH = os.path.join(DATA_DIR, 'lang_settings.json')

SUPPORTED_LANGUAGES = {
    'ar': 'العربية',
    'en': 'English',
    'tr': 'Türkçe',
    'es': 'Español',
    'fr': 'Français',
    'ru': 'Русский',
    'ko': '한국어',
}

TRANSLATIONS = {
    'en': {
        'bot_not_playing': 'Nothing is playing right now.',
        'now_playing_title': 'Now Playing',
        'requested_by': 'Requested by',
        'status': 'Status',
        'next_track': 'Next track',
        'source': 'Source',
        'duration': 'Duration',
        'language_changed': 'Bot language changed to: {language}',
        'language_invalid': 'Unsupported language. Available: {languages}',
        'current_language': 'Current language: {language}',
    },
    'ar': {
        'bot_not_playing': 'لا يوجد شيء يعمل الآن.',
        'now_playing_title': 'يعمل الآن',
        'requested_by': 'مطلوبة بواسطة',
        'status': 'الحالة',
        'next_track': 'التراك التالي',
        'source': 'المصدر',
        'duration': 'المدة',
        'language_changed': 'تم تغيير لغة البوت إلى: {language}',
        'language_invalid': 'اللغة غير مدعومة. المتاح: {languages}',
        'current_language': 'لغة البوت الحالية: {language}',
    },
    'tr': {
        'bot_not_playing': 'Şu anda çalan bir şey yok.',
        'now_playing_title': 'Şimdi Çalıyor',
        'requested_by': 'İsteyen',
        'status': 'Durum',
        'next_track': 'Sonraki parça',
        'source': 'Kaynak',
        'duration': 'Süre',
        'language_changed': 'Bot dili değiştirildi: {language}',
        'language_invalid': 'Desteklenmeyen dil. Mevcut: {languages}',
        'current_language': 'Geçerli bot dili: {language}',
    },
    'es': {
        'bot_not_playing': 'No hay nada reproduciéndose الآن.',
        'now_playing_title': 'Reproduciendo ahora',
        'requested_by': 'Solicitado por',
        'status': 'Estado',
        'next_track': 'Siguiente pista',
        'source': 'Fuente',
        'duration': 'Duración',
        'language_changed': 'El idioma del bot se cambió a: {language}',
        'language_invalid': 'Idioma no compatible. Disponibles: {languages}',
        'current_language': 'Idioma actual del bot: {language}',
    },
    'fr': {
        'bot_not_playing': 'Rien n’est en cours de lecture.',
        'now_playing_title': 'Lecture en cours',
        'requested_by': 'Demandé par',
        'status': 'Statut',
        'next_track': 'Piste suivante',
        'source': 'Source',
        'duration': 'Durée',
        'language_changed': 'La langue du bot a été changée en : {language}',
        'language_invalid': 'Langue non prise en charge. Disponibles : {languages}',
        'current_language': 'Langue actuelle du bot : {language}',
    },
    'ru': {
        'bot_not_playing': 'Сейчас ничего не воспроизводится.',
        'now_playing_title': 'Сейчас играет',
        'requested_by': 'Запросил',
        'status': 'Статус',
        'next_track': 'Следующий трек',
        'source': 'Источник',
        'duration': 'Длительность',
        'language_changed': 'Язык бота изменён на: {language}',
        'language_invalid': 'Язык не поддерживается. Доступно: {languages}',
        'current_language': 'Текущий язык бота: {language}',
    },
    'ko': {
        'bot_not_playing': '현재 재생 중인 항목이 없습니다.',
        'now_playing_title': '현재 재생 중',
        'requested_by': '요청자',
        'status': '상태',
        'next_track': '다음 트랙',
        'source': '출처',
        'duration': '길이',
        'language_changed': '봇 언어가 변경되었습니다: {language}',
        'language_invalid': '지원되지 않는 언어입니다. 사용 가능: {languages}',
        'current_language': '현재 봇 언어: {language}',
    },
}


def _load_json(path: str, default: Any):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data: Any):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_language() -> str:
    data = _load_json(LANG_SETTINGS_PATH, {'language': 'ar'})
    lang = data.get('language', 'ar')
    return lang if lang in SUPPORTED_LANGUAGES else 'ar'


def set_language(lang: str) -> bool:
    if lang not in SUPPORTED_LANGUAGES:
        return False
    _save_json(LANG_SETTINGS_PATH, {'language': lang})
    return True


def t(key: str, lang: str | None = None, **kwargs) -> str:
    lang = lang or get_language()
    lang_map = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    text = lang_map.get(key, TRANSLATIONS['en'].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def format_duration(seconds):
    if not seconds:
        return 'Unknown'
    try:
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f'{h:02}:{m:02}:{s:02}'
        return f'{m:02}:{s:02}'
    except Exception:
        return 'Unknown'
