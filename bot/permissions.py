def normalize(username: str) -> str:
    return username.strip().lstrip('@').lower()


def is_owner(username: str, owner_username: str) -> bool:
    return normalize(username) == normalize(owner_username)


def has_active_role(role_expiries: dict, username: str, role_name: str) -> bool:
    import time
    user_roles = role_expiries.get(normalize(username), {})
    return int(user_roles.get(role_name.lower(), 0)) > int(time.time())


def is_dj(username: str, owner_username: str, djs: list[str], role_expiries: dict | None = None) -> bool:
    uname = normalize(username)
    if uname == normalize(owner_username):
        return True
    if uname in [normalize(x) for x in djs]:
        return True
    if role_expiries and has_active_role(role_expiries, username, 'dj'):
        return True
    return False
