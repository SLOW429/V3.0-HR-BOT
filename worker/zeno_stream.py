import subprocess
from config import ZENO_SERVER, ZENO_PORT, ZENO_MOUNT, ZENO_USERNAME, ZENO_PASSWORD


def build_icecast_url():
    return f'icecast://{ZENO_USERNAME}:{ZENO_PASSWORD}@{ZENO_SERVER}:{ZENO_PORT}/{ZENO_MOUNT}'


def stream_file_to_zeno(file_path: str):
    icecast_url = build_icecast_url()
    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'warning',
        '-re',
        '-i', file_path,
        '-vn',
        '-c:a', 'libmp3lame',
        '-b:a', '128k',
        '-ar', '44100',
        '-ac', '2',
        '-content_type', 'audio/mpeg',
        '-f', 'mp3',
        icecast_url,
    ]
    return subprocess.Popen(cmd)
