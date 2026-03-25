import json
import os
import random
import time
from pathlib import Path

from config import QUEUE_PATH, LIB_PATH, STATE_PATH, CONTROL_PATH, CACHE_DIR, CACHE_INDEX_PATH, HISTORY_PATH
from downloader import download_song, load_json as load_index, save_json as save_index
from zeno_stream import stream_file_to_zeno

BASE_DIR = Path(__file__).resolve().parent.parent
LOCK_PATH = BASE_DIR / 'data' / 'worker.lock'
LAST_AUTODJ_TITLE = None


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


def is_pid_running(pid: int) -> bool:
    try:
        if os.name == 'nt':
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
            if handle == 0:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def acquire_lock():
    if LOCK_PATH.exists():
        try:
            old_pid = int(LOCK_PATH.read_text(encoding='utf-8').strip())
        except Exception:
            old_pid = None
        if old_pid and is_pid_running(old_pid):
            print(f'Worker already running. Existing lock PID: {old_pid}')
            return False
        try:
            LOCK_PATH.unlink()
        except Exception:
            pass
    LOCK_PATH.write_text(str(os.getpid()), encoding='utf-8')
    return True


def release_lock():
    try:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()
    except Exception:
        pass


def update_state(status, title=None, requested_by=None, meta=None, next_title=None):
    save_json(STATE_PATH, {
        'status': status,
        'title': title,
        'requested_by': requested_by,
        'timestamp': int(time.time()),
        'meta': meta or {},
        'next_title': next_title,
    })


def read_control():
    return load_json(CONTROL_PATH, {'action': None})


def clear_control():
    save_json(CONTROL_PATH, {'action': None})


def pop_next_queue_item():
    queue = load_json(QUEUE_PATH, [])
    if not queue:
        return None
    item = queue.pop(0)
    save_json(QUEUE_PATH, queue)
    return item


def peek_next_queue_title():
    queue = load_json(QUEUE_PATH, [])
    if queue:
        return queue[0].get('query', '').strip()
    return None


def append_library(title):
    lib = load_json(LIB_PATH, [])
    if title not in lib:
        lib.append(title)
    lib = lib[-100:]
    save_json(LIB_PATH, lib)


def append_history(title, requested_by):
    history = load_json(HISTORY_PATH, [])
    history.append({'title': title, 'requested_by': requested_by, 'timestamp': int(time.time())})
    save_json(HISTORY_PATH, history[-30:])


def cleanup_cache(max_files=20, max_size_mb=1000):
    files = []
    for entry in CACHE_DIR.glob('*'):
        if entry.is_file():
            try:
                stat = entry.stat()
                files.append({'path': entry, 'mtime': stat.st_mtime, 'size': stat.st_size})
            except Exception:
                pass
    files.sort(key=lambda x: x['mtime'], reverse=True)
    for old_file in files[max_files:]:
        try:
            old_file['path'].unlink()
        except Exception:
            pass

    files = []
    for entry in CACHE_DIR.glob('*'):
        if entry.is_file():
            try:
                stat = entry.stat()
                files.append({'path': entry, 'mtime': stat.st_mtime, 'size': stat.st_size})
            except Exception:
                pass
    files.sort(key=lambda x: x['mtime'])
    max_size_bytes = max_size_mb * 1024 * 1024
    current_size = sum(x['size'] for x in files)
    while current_size > max_size_bytes and files:
        victim = files.pop(0)
        try:
            victim['path'].unlink()
            current_size -= victim['size']
        except Exception:
            pass

    existing = {str(p) for p in CACHE_DIR.glob('*') if p.is_file()}
    index = load_index(CACHE_INDEX_PATH, {})
    changed = False
    for key in list(index.keys()):
        if index[key].get('file_path') not in existing:
            del index[key]
            changed = True
    if changed:
        save_index(CACHE_INDEX_PATH, index)


def pick_random_library_track():
    global LAST_AUTODJ_TITLE
    lib = load_json(LIB_PATH, [])
    if not lib:
        return None
    candidates = [x for x in lib if x != LAST_AUTODJ_TITLE]
    if not candidates:
        candidates = lib[:]
    chosen = random.choice(candidates)
    LAST_AUTODJ_TITLE = chosen
    return chosen


def wait_with_control(proc, title, requested_by, meta, next_title):
    while True:
        ret = proc.poll()
        if ret is not None:
            if ret == 0:
                return 'ended'
            return 'failed'
        control = read_control()
        action = control.get('action')
        if action == 'skip':
            try:
                proc.kill()
            except Exception:
                pass
            clear_control()
            update_state('skipped', title, requested_by, meta, next_title)
            return 'skip'
        if action == 'stop':
            try:
                proc.kill()
            except Exception:
                pass
            clear_control()
            update_state('stopped', title, requested_by, meta, next_title)
            return 'stop'
        time.sleep(0.15)


def main():
    if not acquire_lock():
        return
    print('Stream worker started.')
    clear_control()
    try:
        while True:
            try:
                item = pop_next_queue_item()
                if item:
                    query = item.get('query', '').strip()
                    requested_by = item.get('user', '')
                else:
                    query = pick_random_library_track()
                    requested_by = 'AutoDJ'
                if not query:
                    update_state('idle', None, None, {}, None)
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(3)
                    continue
                next_title = peek_next_queue_title() or pick_random_library_track()
                update_state('starting', query, requested_by, {}, next_title)
                print(f'Downloading: {query}')
                song = download_song(query)
                if not song:
                    print(f'Download failed: {query}')
                    update_state('download_failed', query, requested_by, {}, next_title)
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(2)
                    continue
                title = song['title']
                file_path = song['file_path']
                if not os.path.exists(file_path):
                    print(f'Missing local file after download: {file_path}')
                    update_state('download_failed', title, requested_by, {}, next_title)
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(2)
                    continue
                meta = {
                    'duration': song.get('duration'),
                    'webpage_url': song.get('webpage_url', ''),
                    'uploader': song.get('uploader', ''),
                    'view_count': song.get('view_count', 0),
                    'upload_date': song.get('upload_date', ''),
                    'thumbnail': song.get('thumbnail', ''),
                }
                print(f'Now streaming: {title}')
                update_state('playing', title, requested_by, meta, next_title)
                append_library(title)
                append_history(title, requested_by)
                if next_title and next_title != title:
                    try:
                        download_song(next_title)
                    except Exception as preload_error:
                        print(f'Preload failed for {next_title}: {preload_error}')
                proc = stream_file_to_zeno(file_path)
                outcome = wait_with_control(proc, title, requested_by, meta, next_title)
                if outcome == 'stop':
                    update_state('idle', None, None, {}, None)
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(0.5)
                    continue
                if outcome == 'skip':
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(0.5)
                    continue
                if outcome == 'failed':
                    print(f'Stream failed: {title}')
                    update_state('stream_failed', title, requested_by, meta, next_title)
                    cleanup_cache(max_files=20, max_size_mb=1000)
                    time.sleep(1)
                    continue
                update_state('ended', title, requested_by, meta, next_title)
                cleanup_cache(max_files=20, max_size_mb=1000)
                time.sleep(1.2)
            except Exception as e:
                print(f'Worker error: {e}')
                update_state('error', str(e), None, {}, None)
                time.sleep(3)
    finally:
        release_lock()


if __name__ == '__main__':
    main()
