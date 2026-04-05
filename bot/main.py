import asyncio
import time
from pathlib import Path

from highrise import BaseBot
from highrise.__main__ import main, BotDefinition
from highrise.models import Position

from config import BOT_TOKEN, ROOM_ID, OWNER_USERNAMES
from storage import load_json, save_json
from permissions import is_owner, is_dj, normalize
from styles import ok, warn, error, info, accent, title
from i18n import (
    get_language,
    set_language,
    tr,
    SUPPORTED_LANGUAGES,
    normalize_language_code,
    available_languages_text,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

STATE_PATH = str(DATA_DIR / 'state.json')
ROLES_PATH = str(DATA_DIR / 'roles.json')
QUEUE_PATH = str(DATA_DIR / 'queue.json')
LIB_PATH = str(DATA_DIR / 'library.json')
CONTROL_PATH = str(DATA_DIR / 'control.json')
POINTS_PATH = str(DATA_DIR / 'points.json')
HISTORY_PATH = str(DATA_DIR / 'history.json')

DEFAULT_ROLES = {'djs': [], 'role_expiries': {}}
DEFAULT_QUEUE = []
DEFAULT_LIB = []
DEFAULT_CONTROL = {'action': None}
DEFAULT_POINTS = {'points': {}, 'last_daily': {}, 'last_chat_reward': {}, 'last_active': {}, 'users': {}}
DEFAULT_HISTORY = []
DJ_PRICE = 3000
DJ_DAYS = 7
DAILY_REWARD = 30
MESSAGE_COOLDOWN = 120
MESSAGE_POINTS = 4


def shorten(text: str, limit: int) -> str:
    text = (text or '').strip()
    if len(text) <= limit:
        return text
    return text[:limit - 3] + '...'


def merge_dicts(base: dict, override: dict):
    merged = base.copy()
    merged.update(override)
    return merged


class RadioBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.roles = merge_dicts(DEFAULT_ROLES, load_json(ROLES_PATH, DEFAULT_ROLES))
        self.roles.setdefault('djs', [])
        self.roles.setdefault('role_expiries', {})
        self.queue = load_json(QUEUE_PATH, DEFAULT_QUEUE)
        self.library = load_json(LIB_PATH, DEFAULT_LIB)
        self.points = merge_dicts(DEFAULT_POINTS, load_json(POINTS_PATH, DEFAULT_POINTS))
        self.points.setdefault('points', {})
        self.points.setdefault('last_daily', {})
        self.points.setdefault('last_chat_reward', {})
        self.points.setdefault('last_active', {})
        self.points.setdefault('users', {})
        self.history = load_json(HISTORY_PATH, DEFAULT_HISTORY)

    def lang(self) -> str:
        return get_language()

    def t(self, key: str, **kwargs) -> str:
        return tr(key, self.lang(), **kwargs)

    def save_all(self):
        save_json(ROLES_PATH, self.roles)
        save_json(QUEUE_PATH, self.queue)
        save_json(LIB_PATH, self.library)
        save_json(POINTS_PATH, self.points)
        save_json(HISTORY_PATH, self.history[-30:])

    def get_points(self, user_id: str) -> int:
        return int(self.points.setdefault('points', {}).get(user_id, 0))

    def add_points(self, user_id: str, amount: int) -> int:
        current = self.get_points(user_id)
        self.points.setdefault('points', {})[user_id] = max(0, current + int(amount))
        self.save_all()
        return self.get_points(user_id)

    def spend_points(self, user_id: str, amount: int) -> bool:
        if self.get_points(user_id) < amount:
            return False
        self.add_points(user_id, -amount)
        return True

    def grant_role(self, username: str, role_name: str, days: int):
        user_key = normalize(username)
        expiries = self.roles.setdefault('role_expiries', {})
        user_roles = expiries.setdefault(user_key, {})
        now = int(time.time())
        current_expiry = int(user_roles.get(role_name, 0))
        base = current_expiry if current_expiry > now else now
        user_roles[role_name] = base + (days * 86400)
        self.save_all()

    def prune_expired_roles(self):
        changed = False
        now = int(time.time())
        expiries = self.roles.setdefault('role_expiries', {})
        for user_key in list(expiries.keys()):
            roles = expiries[user_key]
            for role_name in list(roles.keys()):
                if int(roles[role_name]) <= now:
                    del roles[role_name]
                    changed = True
            if not roles:
                del expiries[user_key]
                changed = True
        if changed:
            self.save_all()

    def get_active_roles(self, username: str):
        self.prune_expired_roles()
        return self.roles.get('role_expiries', {}).get(normalize(username), {})

    def user_is_dj(self, username: str) -> bool:
        return is_dj(username, OWNER_USERNAMES, self.roles['djs'], self.roles.get('role_expiries', {}))

    async def on_start(self, session_metadata):
        print('Radio bot started.')
        try:
            await self.highrise.teleport(session_metadata.user_id, Position(16.0, 0.25, 26.0, 'FrontLeft'))
        except Exception as e:
            print(f'Bot teleport error: {e}')

    async def on_chat(self, user, message):
        try:
            msg = message.strip()
            msg_cf = msg.casefold()
            uname = user.username
            uid = user.id

            self.points.setdefault('users', {})[normalize(uname)] = uid

            now_ts = int(time.time())
            self.points.setdefault('last_active', {})[uid] = now_ts

            last_reward = int(self.points.setdefault('last_chat_reward', {}).get(uid, 0))
            if now_ts - last_reward >= MESSAGE_COOLDOWN:
                self.add_points(uid, MESSAGE_POINTS)
                self.points['last_chat_reward'][uid] = now_ts
                self.save_all()
            else:
                self.save_all()

            if msg_cf.startswith('dj add'):
                if not is_owner(uname, OWNER_USERNAMES):
                    await self.highrise.chat(error(self.t('permission_denied')))
                    return
                parts = msg.split()
                if len(parts) < 3:
                    await self.highrise.chat(error(self.t('dj_add_usage')))
                    return
                target = normalize(parts[-1])
                if target not in self.roles['djs']:
                    self.roles['djs'].append(target)
                    self.save_all()
                await self.highrise.chat('\n'.join([ok(self.t('dj_added')), info(f'@{target}')]))
                return

            if msg_cf.startswith('addpoints'):
                if not is_owner(uname, OWNER_USERNAMES):
                    await self.highrise.chat(error(self.t('permission_denied')))
                    return

                parts = msg.split()
                if len(parts) < 3:
                    await self.highrise.chat(error('Usage: addpoints @user amount'))
                    return

                target_name = normalize(parts[1])

                try:
                    amount = int(parts[2])
                except ValueError:
                    await self.highrise.chat(error('Amount must be a number.'))
                    return

                users_map = self.points.setdefault('users', {})
                target_id = users_map.get(target_name)

                if not target_id:
                    await self.highrise.chat(error('User must chat first so the bot can store their ID.'))
                    return

                total = self.add_points(target_id, amount)
                await self.highrise.chat(ok(f'Added {amount} points to @{target_name}. Total: {total}'))
                return

            if msg_cf.startswith('dj del'):
                if not is_owner(uname, OWNER_USERNAMES):
                    await self.highrise.chat(error(self.t('permission_denied')))
                    return
                parts = msg.split()
                if len(parts) < 3:
                    await self.highrise.chat(error(self.t('dj_del_usage')))
                    return
                target = normalize(parts[-1])
                self.roles['djs'] = [x for x in self.roles['djs'] if normalize(x) != target]
                self.roles.get('role_expiries', {}).pop(target, None)
                self.save_all()
                await self.highrise.chat('\n'.join([warn(self.t('dj_removed')), info(f'@{target}')]))
                return

            if msg_cf == 'dj list':
                djs = ', '.join(self.roles['djs']) if self.roles['djs'] else self.t('none')
                await self.highrise.chat('\n'.join([title(self.t('dj_list_title')), info(djs)]))
                return

            if msg_cf in {'points', 'رصيدي', 'فلوسي'}:
                await self.highrise.chat(ok(self.t('your_points', points=self.get_points(uid))))
                return

            if msg_cf in {'daily', 'يومي'}:
                last_daily = int(self.points.setdefault('last_daily', {}).get(uid, 0))
                if now_ts - last_daily < 86400:
                    remaining = 86400 - (now_ts - last_daily)
                    await self.highrise.chat(
                        warn(self.t('daily_ready_in', hours=remaining // 3600, minutes=(remaining % 3600) // 60))
                    )
                    return
                self.points['last_daily'][uid] = now_ts
                total = self.add_points(uid, DAILY_REWARD)
                await self.highrise.chat(
                    '\n'.join([
                        ok(self.t('daily_claimed', points=DAILY_REWARD)),
                        info(self.t('your_points_now', points=total))
                    ])
                )
                return

            if msg_cf in {'shop', 'المتجر'}:
                await self.highrise.chat(
                    '\n'.join([
                        title(self.t('shop_title')),
                        info(self.t('shop_dj_item', days=DJ_DAYS, price=DJ_PRICE))
                    ])
                )
                return

            if msg_cf in {'buy dj', 'شراء dj'}:
                if not self.spend_points(uid, DJ_PRICE):
                    await self.highrise.chat(
                        error(self.t('points_not_enough', price=DJ_PRICE, points=self.get_points(uid)))
                    )
                    return
                self.grant_role(uname, 'dj', DJ_DAYS)
                await self.highrise.chat(
                    '\n'.join([
                        ok(self.t('buy_dj_success', days=DJ_DAYS)),
                        info(self.t('your_points_now', points=self.get_points(uid)))
                    ])
                )
                return

            if msg_cf in {'myroles', 'رتبي'}:
                roles = self.get_active_roles(uname)
                if not roles:
                    await self.highrise.chat(warn(self.t('no_roles')))
                    return
                lines = [title(self.t('your_roles'))]
                for role_name, expiry in roles.items():
                    remaining = max(0, int(expiry) - now_ts)
                    lines.append(info(f'{role_name.upper()} - {self.t("days_left", days=remaining // 86400)}'))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg_cf in {'top', 'leaderboard', 'توب'}:
                top_users = sorted(
                    self.points.get('points', {}).items(),
                    key=lambda x: int(x[1]),
                    reverse=True
                )[:10]
                if not top_users:
                    await self.highrise.chat(warn(self.t('no_leaderboard')))
                    return

                users_map = self.points.get('users', {})
                reverse_users_map = {v: k for k, v in users_map.items()}

                lines = [title(self.t('top_points'))]
                for idx, (user_id, pts) in enumerate(top_users, start=1):
                    display_name = reverse_users_map.get(user_id, user_id)
                    lines.append(info(f'{idx}. @{display_name} - {pts}'))

                await self.highrise.chat('\n'.join(lines))
                return

            if msg_cf in {'lang', 'language', 'لغة', 'dil'}:
                current = SUPPORTED_LANGUAGES[self.lang()]
                await self.highrise.chat(
                    '\n'.join([
                        title(self.t('language_title')),
                        info(self.t('current_language', language=current)),
                        accent(available_languages_text()),
                    ])
                )
                return

            if (
                msg_cf.startswith('lang ')
                or msg_cf.startswith('language ')
                or msg_cf.startswith('لغة ')
                or msg_cf.startswith('dil ')
            ):
                raw_target = msg.split(maxsplit=1)[1].strip() if len(msg.split(maxsplit=1)) > 1 else ''
                code = normalize_language_code(raw_target)
                if not code or code not in SUPPORTED_LANGUAGES:
                    await self.highrise.chat(error(self.t('language_invalid', languages=available_languages_text())))
                    return
                set_language(code)
                await self.highrise.chat(ok(tr('language_changed', code, language=SUPPORTED_LANGUAGES[code])))
                return

            if msg.startswith('-play'):
                if not self.user_is_dj(uname):
                    await self.highrise.chat(error(self.t('dj_required')))
                    return
                query = msg.replace('-play', '', 1).strip()
                if not query:
                    await self.highrise.chat(error(self.t('play_usage')))
                    return
                self.queue.append({'user': uname, 'query': query})
                self.save_all()
                await self.highrise.chat(
                    '\n'.join([
                        ok(self.t('track_added')),
                        title(f'🎵 {shorten(query, 38)}'),
                        info(f'👤 {self.t("by_user", user=shorten(uname, 18))}')
                    ])
                )
                return

            if msg_cf == '-queue':
                if not self.queue:
                    await self.highrise.chat(warn(self.t('queue_empty')))
                    return
                lines = [title(self.t('queue_title'))]
                for i, item in enumerate(self.queue[:8], start=1):
                    lines.append(info(f"{i}. {shorten(item['query'], 34)} - @{shorten(item['user'], 14)}"))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg_cf.startswith('-remove '):
                if not self.user_is_dj(uname):
                    await self.highrise.chat(error(self.t('dj_required')))
                    return
                try:
                    idx = int(msg.split()[1]) - 1
                    removed = self.queue.pop(idx)
                    self.save_all()
                    await self.highrise.chat(warn(self.t('removed_track', title=shorten(removed['query'], 28))))
                except Exception:
                    await self.highrise.chat(error(self.t('queue_invalid_number')))
                return

            if msg_cf.startswith('-move '):
                if not self.user_is_dj(uname):
                    await self.highrise.chat(error(self.t('dj_required')))
                    return
                try:
                    _, a, b = msg.split()
                    src = int(a) - 1
                    dst = int(b) - 1
                    item = self.queue.pop(src)
                    self.queue.insert(dst, item)
                    self.save_all()
                    await self.highrise.chat(ok(self.t('queue_move_ok')))
                except Exception:
                    await self.highrise.chat(error(self.t('queue_move_usage')))
                return

            if msg_cf == '-np':
                state = load_json(STATE_PATH, {})
                status = state.get('status')
                title_text = state.get('title')
                requested_by = state.get('requested_by')
                meta = state.get('meta', {})
                next_title = state.get('next_title')
                if status not in ('starting', 'playing', 'ended') or not title_text:
                    await self.highrise.chat(warn(self.t('nothing_playing')))
                    return
                duration = meta.get('duration')
                views = meta.get('view_count', 0)
                uploader = shorten(meta.get('uploader', 'Unknown'), 18)
                if isinstance(duration, int):
                    duration_text = f'{duration // 60}:{duration % 60:02d}'
                else:
                    duration_text = 'Unknown'
                try:
                    views_num = int(views)
                    if views_num >= 1_000_000:
                        views_text = f'{views_num / 1_000_000:.1f}M'
                    elif views_num >= 1_000:
                        views_text = f'{views_num / 1_000:.1f}K'
                    else:
                        views_text = str(views_num)
                except Exception:
                    views_text = 'Unknown'
                lines = [
                    title(f'♪ {self.t("now_playing")}'),
                    info(shorten(title_text, 34)),
                    accent(f'👤 {uploader} • 👁 {views_text}'),
                    ok(f'⏱ {duration_text} • 🎧 {shorten(requested_by or "Unknown", 16)}'),
                ]
                if next_title:
                    lines.append(warn(f'▶ {self.t("up_next")}: {shorten(next_title, 28)}'))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg_cf == '-history':
                history = load_json(HISTORY_PATH, DEFAULT_HISTORY)
                if not history:
                    await self.highrise.chat(warn(self.t('history_empty')))
                    return
                lines = [title(self.t('history_title'))]
                for item in history[-5:][::-1]:
                    lines.append(info(shorten(item.get('title', ''), 34)))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg_cf == '-songlink':
                state = load_json(STATE_PATH, {})
                url = state.get('meta', {}).get('webpage_url', '')
                if not url:
                    await self.highrise.send_whisper(user.id, self.t('song_link_missing'))
                    return
                await self.highrise.send_whisper(user.id, url)
                return

            if msg_cf == '-clear':
                if not is_owner(uname, OWNER_USERNAMES):
                    await self.highrise.chat(error(self.t('permission_denied')))
                    return
                self.queue = []
                self.save_all()
                save_json(CONTROL_PATH, {'action': 'stop', 'by': uname, 'ts': time.time()})
                await self.highrise.chat(
                    '\n'.join([
                        warn(self.t('queue_cleared')),
                        error(self.t('playback_stopped'))
                    ])
                )
                return

            if msg_cf == '-skip':
                if not self.user_is_dj(uname):
                    await self.highrise.chat(error(self.t('dj_required')))
                    return
                state = load_json(STATE_PATH, {})
                current_title = shorten(state.get('title') or 'Unknown', 28)
                queue_now = load_json(QUEUE_PATH, DEFAULT_QUEUE)
                next_title = shorten(queue_now[0].get('query', '').strip(), 28) if queue_now else (state.get('next_title') or 'AutoDJ')
                save_json(CONTROL_PATH, {'action': 'skip', 'by': uname, 'ts': time.time()})
                await self.highrise.chat(
                    '\n'.join([
                        warn(self.t('skip_done')),
                        error(f'⏭ {self.t("current_track")}: {current_title}'),
                        ok(f'▶ {self.t("up_next")}: {shorten(next_title, 28)}'),
                    ])
                )
                return

            if msg_cf == '-stop':
                if not self.user_is_dj(uname):
                    await self.highrise.chat(error(self.t('dj_required')))
                    return
                save_json(CONTROL_PATH, {'action': 'stop', 'by': uname, 'ts': time.time()})
                await self.highrise.chat('\n'.join([warn(self.t('stop_sent')), info(self.t('stop_wait'))]))
                return

            if msg_cf == '-library':
                if not self.library:
                    await self.highrise.chat(warn(self.t('library_empty')))
                    return
                lines = [title(self.t('library_title'))]
                for i, name in enumerate(self.library[-8:], start=1):
                    lines.append(info(f'{i}. {shorten(name, 34)}'))
                await self.highrise.chat('\n'.join(lines))
                return

        except Exception as e:
            try:
                await self.highrise.send_whisper(user.id, self.t('command_error', error=str(e)))
            except Exception:
                pass
            print(f'[on_chat error] {e}')


async def run_bot_forever():
    while True:
        try:
            await main([BotDefinition(RadioBot(), ROOM_ID, BOT_TOKEN)])
        except Exception as e:
            print('Radio bot crashed, restarting in 5 seconds...', e)
            await asyncio.sleep(5)


if not BOT_TOKEN or not ROOM_ID:
    print('Missing ENV')
else:
    asyncio.run(run_bot_forever())