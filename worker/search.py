import yt_dlp


def search_youtube_audio(query: str):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "format": "bestaudio/best",
        "noplaylist": True,
        "extract_flat": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        if not info:
            return None

        if "entries" in info:
            entries = info.get("entries") or []
            if not entries:
                return None
            info = entries[0]

        formats = info.get("formats", [])
        audio_url = None

        for f in reversed(formats):
            if f.get("acodec") != "none" and f.get("url"):
                audio_url = f["url"]
                break

        if not audio_url:
            audio_url = info.get("url")

        if not audio_url:
            return None

        return {
            "title": info.get("title", query),
            "webpage_url": info.get("webpage_url", ""),
            "duration": info.get("duration"),
            "audio_url": audio_url,
        }