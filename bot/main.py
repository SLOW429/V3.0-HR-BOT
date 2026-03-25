import asyncio
import time
from pathlib import Path

from highrise import BaseBot
from highrise.__main__ import main, BotDefinition
from highrise.models import Position

from config import BOT_TOKEN, ROOM_ID, OWNER_USERNAME
from storage import load_json, save_json
from permissions import is_owner, is_dj, normalize
from styles import ok, warn, error, info, accent, title

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
DEFAULT_POINTS = {'points': {}, 'last_daily': {}, 'last_chat_reward': {}, 'last_active': {}}
DEFAULT_HISTORY = []
DJ_PRICE = 3500
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
        self.queue = load_json(QUEUE_PATH, DEFAULT_QUEUE)
        self.library = load_json(LIB_PATH, DEFAULT_LIB)
        self.points = merge_dicts(DEFAULT_POINTS, load_json(POINTS_PATH, DEFAULT_POINTS))
        self.history = load_json(HISTORY_PATH, DEFAULT_HISTORY)

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

    async def on_start(self, session_metadata):
        print('Radio bot started.')
        try:
            await self.highrise.teleport(session_metadata.user_id, Position(16.5, 13.5, 1.5, 'FrontLeft'))
        except Exception as e:
            print(f'Bot teleport error: {e}')

    async def on_chat(self, user, message):
        try:
            msg = message.strip()
            uname = user.username
            uid = user.id
            now_ts = int(time.time())
            self.points.setdefault('last_active', {})[uid] = now_ts
            last_reward = int(self.points.setdefault('last_chat_reward', {}).get(uid, 0))
            if now_ts - last_reward >= MESSAGE_COOLDOWN:
                self.add_points(uid, MESSAGE_POINTS)
                self.points['last_chat_reward'][uid] = now_ts
                self.save_all()

            if msg.startswith('dj add'):
                if not is_owner(uname, OWNER_USERNAME):
                    return
                parts = msg.split()
                if len(parts) < 3:
                    await self.highrise.chat(error('اكتب: dj add @user'))
                    return
                target = normalize(parts[-1])
                if target not in self.roles['djs']:
                    self.roles['djs'].append(target)
                    self.save_all()
                await self.highrise.chat('\n'.join([ok('تمت إضافة DJ جديد'), info(f'@{target}')]))
                return

            if msg.startswith('dj del'):
                if not is_owner(uname, OWNER_USERNAME):
                    return
                parts = msg.split()
                if len(parts) < 3:
                    await self.highrise.chat(error('اكتب: dj del @user'))
                    return
                target = normalize(parts[-1])
                self.roles['djs'] = [x for x in self.roles['djs'] if x != target]
                self.save_all()
                await self.highrise.chat('\n'.join([warn('تم حذف DJ'), info(f'@{target}')]))
                return

            if msg == 'dj list':
                djs = ', '.join(self.roles['djs']) if self.roles['djs'] else 'لا يوجد'
                await self.highrise.chat('\n'.join([title('DJ LIST'), info(djs)]))
                return

            if msg.casefold() in {'points', 'رصيدي', 'فلوسي'}:
                await self.highrise.chat(ok(f'رصيدك: {self.get_points(uid)} نقطة'))
                return

            if msg.casefold() in {'daily', 'يومي'}:
                last_daily = int(self.points.setdefault('last_daily', {}).get(uid, 0))
                if now_ts - last_daily < 86400:
                    remaining = 86400 - (now_ts - last_daily)
                    await self.highrise.chat(warn(f'اليومي جاهز بعد {remaining // 3600} ساعة و {(remaining % 3600) // 60} دقيقة'))
                    return
                self.points['last_daily'][uid] = now_ts
                total = self.add_points(uid, DAILY_REWARD)
                await self.highrise.chat('\n'.join([ok(f'أخذت {DAILY_REWARD} نقطة يومية'), info(f'رصيدك الآن: {total}')]))
                return

            if msg.casefold() in {'shop', 'المتجر'}:
                await self.highrise.chat('\n'.join([
                    title('RADIO SHOP'),
                    info(f'DJ لمدة {DJ_DAYS} أيام = {DJ_PRICE} نقطة'),
                ]))
                return

            if msg.casefold() in {'buy dj', 'شراء dj'}:
                if not self.spend_points(uid, DJ_PRICE):
                    await self.highrise.chat(error(f'نقاطك غير كافية. السعر: {DJ_PRICE} | رصيدك: {self.get_points(uid)}'))
                    return
                self.grant_role(uname, 'dj', DJ_DAYS)
                await self.highrise.chat('\n'.join([ok(f'تم شراء DJ لمدة {DJ_DAYS} أيام'), info(f'رصيدك الآن: {self.get_points(uid)}')]))
                return

            if msg.casefold() in {'myroles', 'رتبي'}:
                roles = self.get_active_roles(uname)
                if not roles:
                    await self.highrise.chat(warn('لا تملك أي رتب حالياً'))
                    return
                lines = [title('YOUR ROLES')]
                for role_name, expiry in roles.items():
                    remaining = max(0, int(expiry) - now_ts)
                    lines.append(info(f'{role_name.upper()} - {remaining // 86400} يوم'))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg.casefold() in {'top', 'leaderboard', 'توب'}:
                top_users = sorted(self.points.get('points', {}).items(), key=lambda x: int(x[1]), reverse=True)[:10]
                if not top_users:
                    await self.highrise.chat(warn('لا يوجد ترتيب بعد'))
                    return
                lines = [title('TOP POINTS')]
                for idx, (user_id, pts) in enumerate(top_users, start=1):
                    lines.append(info(f'{idx}. {user_id} - {pts}'))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg.startswith('-play'):
                if not is_dj(uname, OWNER_USERNAME, self.roles['djs'], self.roles.get('role_expiries', {})):
                    await self.highrise.chat(error('غير مسموح لك'))
                    return
                query = msg.replace('-play', '', 1).strip()
                if not query:
                    await self.highrise.chat(error('اكتب اسم الأغنية بعد -play'))
                    return
                self.queue.append({'user': uname, 'query': query})
                self.save_all()
                await self.highrise.chat('\n'.join([ok('تمت إضافة الأغنية للقائمة'), title(f'🎵 {shorten(query, 38)}'), info(f'👤 بواسطة: {shorten(uname, 18)}')]))
                return

            if msg == '-queue':
                if not self.queue:
                    await self.highrise.chat(warn('لا توجد طلبات'))
                    return
                lines = [title('QUEUE')]
                for i, item in enumerate(self.queue[:8], start=1):
                    lines.append(info(f"{i}. {shorten(item['query'], 34)} - @{shorten(item['user'], 14)}"))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg.startswith('-remove '):
                if not is_dj(uname, OWNER_USERNAME, self.roles['djs'], self.roles.get('role_expiries', {})):
                    return
                try:
                    idx = int(msg.split()[1]) - 1
                    removed = self.queue.pop(idx)
                    self.save_all()
                    await self.highrise.chat(warn(f"تم حذف: {shorten(removed['query'], 28)}"))
                except Exception:
                    await self.highrise.chat(error('اكتب رقم صحيح من الكيو'))
                return

            if msg.startswith('-move '):
                if not is_dj(uname, OWNER_USERNAME, self.roles['djs'], self.roles.get('role_expiries', {})):
                    return
                try:
                    _, a, b = msg.split()
                    src = int(a) - 1
                    dst = int(b) - 1
                    item = self.queue.pop(src)
                    self.queue.insert(dst, item)
                    self.save_all()
                    await self.highrise.chat(ok('تم تعديل ترتيب الكيو'))
                except Exception:
                    await self.highrise.chat(error('استخدام صحيح: -move 3 1'))
                return

            if msg == '-np':
                state = load_json(STATE_PATH, {})
                status = state.get('status')
                title_text = state.get('title')
                requested_by = state.get('requested_by')
                meta = state.get('meta', {})
                next_title = state.get('next_title')
                if status not in ('starting', 'playing', 'ended') or not title_text:
                    await self.highrise.chat(warn('لا يوجد تشغيل حالي'))
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
                    title('♪ NOW PLAYING'),
                    info(shorten(title_text, 34)),
                    accent(f'👤 {uploader} • 👁 {views_text}'),
                    ok(f'⏱ {duration_text} • 🎧 {shorten(requested_by or "Unknown", 16)}'),
                ]
                if next_title:
                    lines.append(warn(f'▶ NEXT: {shorten(next_title, 28)}'))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg == '-history':
                history = load_json(HISTORY_PATH, DEFAULT_HISTORY)
                if not history:
                    await self.highrise.chat(warn('لا يوجد تاريخ تشغيل بعد'))
                    return
                lines = [title('RECENT TRACKS')]
                for item in history[-5:][::-1]:
                    lines.append(info(shorten(item.get('title', ''), 34)))
                await self.highrise.chat('\n'.join(lines))
                return

            if msg == '-songlink':
                state = load_json(STATE_PATH, {})
                url = state.get('meta', {}).get('webpage_url', '')
                if not url:
                    await self.highrise.send_whisper(user.id, 'لا يوجد رابط حالي')
                    return
                await self.highrise.send_whisper(user.id, url)
                return

            if msg == '-clear':
                if not is_owner(uname, OWNER_USERNAME):
                    return
                self.queue = []
                self.save_all()
                save_json(CONTROL_PATH, {'action': 'stop', 'by': uname, 'ts': time.time()})
                await self.highrise.chat('\n'.join([warn('تم مسح القائمة'), error('وتم إيقاف التشغيل الحالي')]))
                return

            if msg == '-skip':
                if not is_dj(uname, OWNER_USERNAME, self.roles['djs'], self.roles.get('role_expiries', {})):
                    return
                state = load_json(STATE_PATH, {})
                current_title = shorten(state.get('title') or 'غير معروف', 28)
                queue_now = load_json(QUEUE_PATH, DEFAULT_QUEUE)
                next_title = shorten(queue_now[0].get('query', '').strip(), 28) if queue_now else (state.get('next_title') or 'AutoDJ')
                save_json(CONTROL_PATH, {'action': 'skip', 'by': uname, 'ts': time.time()})
                await self.highrise.chat('\n'.join([
                    warn('تم تخطي الأغنية الحالية'),
                    error(f'⏭ الحالية: {current_title}'),
                    ok(f'▶ التالية: {shorten(next_title, 28)}'),
                ]))
                return

            if msg == '-stop':
                if not is_dj(uname, OWNER_USERNAME, self.roles['djs'], self.roles.get('role_expiries', {})):
                    return
                save_json(CONTROL_PATH, {'action': 'stop', 'by': uname, 'ts': time.time()})
                await self.highrise.chat('\n'.join([warn('تم إرسال أمر الإيقاف'), info('سيتم إيقاف الأغنية الحالية')]))
                return

            if msg == '-library':
                if not self.library:
                    await self.highrise.chat(warn('المكتبة فارغة'))
                    return
                lines = [title('LIBRARY')]
                for i, name in enumerate(self.library[-8:], start=1):
                    lines.append(info(f'{i}. {shorten(name, 34)}'))
                await self.highrise.chat('\n'.join(lines))
                return
        except Exception as e:
            try:
                await self.highrise.send_whisper(user.id, f'حصل خطأ: {e}')
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
