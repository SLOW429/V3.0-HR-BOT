import hashlib
import json
import os

import yt_dlp

from config import CACHE_DIR, CACHE_INDEX_PATH

CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def make_key(query: str) -> str:
    return hashlib.md5(query.strip().lower().encode('utf-8')).hexdigest()


def get_cached_file(query: str):
    index = load_json(CACHE_INDEX_PATH, {})
    key = make_key(query)
    data = index.get(key)
    if not data:
        return None
    file_path = data.get('file_path')
    if file_path and os.path.exists(file_path):
        return data
    return None


def download_song(query: str):
    cached = get_cached_file(query)
    if cached:
        return cached

    key = make_key(query)
    outtmpl = str(CACHE_DIR / f'{key}.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'extract_flat': False,
        'forceipv4': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'prefer_ffmpeg': True,
        'keepvideo': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            entries = info.get('entries') or []
            if not entries:
                return None
            info = entries[0]
        final_file = str(CACHE_DIR / f'{key}.mp3')
        data = {
            'title': info.get('title', query),
            'duration': info.get('duration'),
            'webpage_url': info.get('webpage_url', ''),
            'file_path': final_file,
            'uploader': info.get('uploader', ''),
            'view_count': info.get('view_count', 0),
            'upload_date': info.get('upload_date', ''),
            'thumbnail': info.get('thumbnail', ''),
            'query': query,
        }
        index = load_json(CACHE_INDEX_PATH, {})
        index[key] = data
        save_json(CACHE_INDEX_PATH, index)
        return data
