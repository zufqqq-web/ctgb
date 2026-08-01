from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_genres, get_movies_by_genre, get_all_movies

admin_reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить жанр"), KeyboardButton(text="❌ Удалить жанр")],
        [KeyboardButton(text="🎬 Добавить фильм"), KeyboardButton(text="🗑 Удалить фильм")],
        [KeyboardButton(text="📋 Посмотреть жанры")],
        [KeyboardButton(text="🎥 Посмотреть фильм"), KeyboardButton(text="🔍 Поиск")]
    ],
    resize_keyboard=True
)

user_reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎥 Посмотреть фильм")],
        [KeyboardButton(text="🔍 Поиск")]
    ],
    resize_keyboard=True
)

def genres_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for gid, name in get_genres():
        builder.button(text=name, callback_data=f"genre_{gid}")
    builder.adjust(1)
    return builder.as_markup()

def movies_by_genre_kb(genre_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for mid, title, *_ in get_movies_by_genre(genre_id):
        builder.button(text=title, callback_data=f"movie_{mid}")
    builder.button(text="⬅️ Назад", callback_data="back_to_genres")
    builder.adjust(1)
    return builder.as_markup()

def delete_movies_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for mid, title in get_all_movies():
        builder.button(text=f"🗑 {title}", callback_data=f"del_mov_{mid}")
    builder.button(text="❌ Отмена", callback_data="cancel_delete")
    builder.adjust(1)
    return builder.as_markup()

def delete_genres_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for gid, name in get_genres():
        builder.button(text=f"❌ {name}", callback_data=f"del_gen_{gid}")
    builder.button(text="❌ Отмена", callback_data="cancel_delete")
    builder.adjust(1)
    return builder.as_markup()

def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])