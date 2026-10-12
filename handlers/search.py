from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from handlers.states import SearchStates
from services.audio_sender import send_audio_from_url
from services.search_cache import get_tracks, save_tracks
from services.site1parser import search

router = Router()

PAGE_SIZE = 6
MAX_TRACKS = 36
STALE_MSG = "Это меню устарело. Сделай новый /search"


# ---------- Вспомогательные функции ----------

def build_keyboard(
    tracks: list[dict],
    page: int,
    search_id: str,
) -> InlineKeyboardMarkup:
    """Собирает инлайн-клавиатуру для указанной страницы."""
    total_pages = (len(tracks) + PAGE_SIZE - 1) // PAGE_SIZE

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_tracks = tracks[start:end]

    rows: list[list[InlineKeyboardButton]] = []

    for i, t in enumerate(page_tracks):
        global_idx = start + i
        label = f"{t['artist']} – {t['title']}"
        rows.append([InlineKeyboardButton(
            text=label[:60],
            callback_data=f"s:trk:{search_id}:{global_idx}",
        )])

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"s:pg:{search_id}:{page - 1}",
        ))
    nav.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}",
        callback_data="s:noop",
    ))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"s:pg:{search_id}:{page + 1}",
        ))
    if nav:
        rows.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_header(query: str, tracks: list[dict], page: int) -> str:
    total_pages = (len(tracks) + PAGE_SIZE - 1) // PAGE_SIZE
    return (
        f"🔍 По запросу «{query}» найдено {len(tracks)} треков.\n"
        f"Страница {page + 1} из {total_pages}.\n\n"
        f"Нажми на трек, чтобы скачать."
    )

async def run_search(message: Message, query: str) -> None:
    status_msg = await message.answer(f"🔍 Ищу: {query}")

    tracks = await search(query, limit=MAX_TRACKS)

    try:
        await status_msg.delete()
    except Exception:
        pass

    if not tracks:
        await message.answer("Ничего не нашлось 😔")
        return

    search_id = save_tracks(message.from_user.id, tracks)
    await message.answer(
        build_header(query, tracks, page=0),
        reply_markup=build_keyboard(tracks, page=0, search_id=search_id),
    )

# ---------- Хэндлеры ----------

@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    query = message.text.removeprefix("/search").strip()

    if not query:
        await message.answer(
            "🔍 Введи название трека — я поищу.\n"
            "Например: <i>radiohead no surprises</i>\n\n"
            "Для отмены: /cancel",
            parse_mode="HTML",
        )
        await state.set_state(SearchStates.waiting_query)
        return

    await state.clear()
    await run_search(message, query)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Если захочешь — снова /search")


@router.message(SearchStates.waiting_query)
async def on_query_entered(message: Message, state: FSMContext):
    query = message.text.strip()
    await state.clear()
    await run_search(message, query)


@router.callback_query(F.data.startswith("s:pg:"))
async def on_page_nav(callback: CallbackQuery):
    _, _, search_id, page_str = callback.data.split(":")
    page = int(page_str)

    tracks = get_tracks(callback.from_user.id, search_id)
    if tracks is None:
        await callback.answer(STALE_MSG, show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=build_keyboard(tracks, page, search_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("s:trk:"))
async def on_track_click(callback: CallbackQuery):
    _, _, search_id, idx_str = callback.data.split(":")
    idx = int(idx_str)

    tracks = get_tracks(callback.from_user.id, search_id)
    if tracks is None or idx >= len(tracks):
        await callback.answer(STALE_MSG, show_alert=True)
        return

    await callback.answer("Скачиваю...")

    # Удаляем меню целиком — оно своё отработало
    try:
        await callback.message.delete()
    except Exception:
        pass

    track = tracks[idx]
    await callback.message.answer(f"🎵 {track['artist']} – {track['title']}")
    await send_audio_from_url(
        callback.message,
        track["url"],
        performer=track["artist"],
        title=track["title"],
        cover_url=track.get("cover_url"),
    )

@router.callback_query(F.data == "s:noop")
async def on_noop(callback: CallbackQuery):
    await callback.answer()