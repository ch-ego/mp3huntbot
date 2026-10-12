def fix_mojibake(s: str) -> str:
    """Лечит двойное декодирование UTF-8 -> Latin-1 (кракозябры в кириллице)."""
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def try_fix_cp1251(s: str) -> str:
    """Если ID3-тег записан как CP1251, а читается как Latin-1 — чиним."""
    # Сначала пробуем latin-1 -> cp1251 (частый случай для русских тегов)
    try:
        return s.encode("latin-1").decode("cp1251")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    # Потом пробуем utf-8 (на случай, если уже всё ок)
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s