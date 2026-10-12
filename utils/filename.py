from email.message import Message as EmailMessage
from urllib.parse import unquote, urlparse
from .encoding import fix_mojibake

def extract_filename(url: str, headers) -> str:
    """Достаёт имя файла: сначала из Content-Disposition, потом из URL."""
    cd = headers.get("Content-Disposition")
    if cd:
        msg = EmailMessage()
        msg["Content-Disposition"] = cd
        name = msg.get_filename()
        if name:
            return fix_mojibake(name)

    path = urlparse(url).path
    name = unquote(path.rsplit("/", 1)[-1])
    return fix_mojibake(name) or "track.mp3"

def split_performer_title(filename: str) -> tuple[str | None, str]:
    """Fallback: разбить имя файла на исполнителя и название."""
    name_no_ext = filename.rsplit(".", 1)[0]
    for sep in [", ", " – ", " - ", "-"]:
        if sep in name_no_ext:
            performer, title = name_no_ext.split(sep, 1)
            return performer.strip(), title.strip()
    return None, name_no_ext
