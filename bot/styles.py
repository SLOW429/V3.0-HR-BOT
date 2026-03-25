def color(hex_color: str, text: str) -> str:
    return f'<#{hex_color}>{text}'


def ok(text: str) -> str:
    return color('8EF7C5', text)


def warn(text: str) -> str:
    return color('FFD166', text)


def error(text: str) -> str:
    return color('FF6B6B', text)


def info(text: str) -> str:
    return color('7AD7FF', text)


def accent(text: str) -> str:
    return color('CBA6F7', text)


def title(text: str) -> str:
    return color('5C7FE8', text)
