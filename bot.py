import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from db import (
    init_db, add_genre, delete_genre, get_genres,
    add_movie, delete_movie, get_movies_by_genre, get_movie_by_id,
    search_movies, get_all_movies
)
from states import AddGenre, AddMovie, DeleteMovie, DeleteGenre
from buttons import (
    admin_reply_kb, user_reply_kb, genres_inline_kb,
    movies_by_genre_kb, delete_movies_kb, delete_genres_kb, cancel_kb
)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("Привет, Админ! 👑", reply_markup=admin_reply_kb)
    else:
        await message.answer("Привет! Хочешь посмотреть кино? 🎬", reply_markup=user_reply_kb)

@dp.message(StateFilter(None), F.text == "🎥 Посмотреть фильм")
async def show_genres(message: Message):
    genres = get_genres()
    if not genres:
        await message.answer("Пока нет ни одного жанра 😢")
        return
    await message.answer("Выбери жанр:", reply_markup=genres_inline_kb())

@dp.message(StateFilter(None), F.text == "🔍 Поиск")
async def ask_search(message: Message):
    await message.answer("Введи название фильма или жанр:", reply_markup=cancel_kb())

@dp.message(StateFilter(None), F.text == "➕ Добавить жанр")
async def add_genre_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS: return
    await state.set_state(AddGenre.waiting_name)
    await message.answer("Введи название жанра:", reply_markup=cancel_kb())

@dp.message(StateFilter(None), F.text == "❌ Удалить жанр")
async def delete_genre_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS: return
    genres = get_genres()
    if not genres:
        await message.answer("Нет жанров для удаления.")
        return
    await state.set_state(DeleteGenre.waiting_choice)
    await message.answer("Выбери жанр для удаления:", reply_markup=delete_genres_kb())

@dp.message(StateFilter(None), F.text == "🎬 Добавить фильм")
async def add_movie_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS: return
    genres = get_genres()
    if not genres:
        await message.answer("Сначала добавь хотя бы один жанр.")
        return
    await state.set_state(AddMovie.choosing_genre)
    await message.answer("Выбери жанр фильма:", reply_markup=genres_inline_kb())

@dp.message(StateFilter(None), F.text == "🗑 Удалить фильм")
async def delete_movie_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS: return
    movies = get_all_movies()
    if not movies:
        await message.answer("Нет фильмов для удаления.")
        return
    await state.set_state(DeleteMovie.waiting_choice)
    await message.answer("Выбери фильм для удаления:", reply_markup=delete_movies_kb())

@dp.message(StateFilter(None), F.text == "📋 Посмотреть жанры")
async def view_genres(message: Message):
    if message.from_user.id not in config.ADMIN_IDS: return
    genres = get_genres()
    if not genres:
        await message.answer("Жанров пока нет.")
        return
    text = "📋 <b>Жанры:</b>\n" + "\n".join(f"• {name}" for _, name in genres)
    await message.answer(text, parse_mode="HTML")

@dp.callback_query(StateFilter(None), F.data.startswith("genre_"))
async def show_movies_in_genre(call: CallbackQuery):
    genre_id = int(call.data.split("_")[1])
    movies = get_movies_by_genre(genre_id)
    if not movies:
        await call.message.answer("В этом жанре пока нет фильмов.")
        await call.answer()
        return
    await call.message.edit_text("Выбери фильм:", reply_markup=movies_by_genre_kb(genre_id))
    await call.answer()

@dp.callback_query(StateFilter(None), F.data == "back_to_genres")
async def back_to_genres(call: CallbackQuery):
    await call.message.edit_text("Выбери жанр:", reply_markup=genres_inline_kb())
    await call.answer()

@dp.callback_query(StateFilter(None), F.data.startswith("movie_"))
async def watch_movie(call: CallbackQuery):
    movie_id = int(call.data.split("_")[1])
    m = get_movie_by_id(movie_id)
    if not m:
        await call.answer("Фильм не найден", show_alert=True)
        return
    _, title, description, year, file_id = m
    caption = f"🎬 <b>{title}</b> ({year})\n\n{description}"
    await call.message.answer_video(video=file_id, caption=caption, parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("del_gen_"))
async def delete_genre_process(call: CallbackQuery, state: FSMContext):
    genre_id = int(call.data.split("_")[2])
    delete_genre(genre_id)
    await call.message.edit_text("Жанр удалён ✅")
    await state.clear()
    await call.answer()

@dp.callback_query(F.data.startswith("del_mov_"))
async def delete_movie_process(call: CallbackQuery, state: FSMContext):
    movie_id = int(call.data.split("_")[2])
    delete_movie(movie_id)
    await call.message.edit_text("Фильм удалён ✅")
    await state.clear()
    await call.answer()

@dp.callback_query(F.data == "cancel")
async def cancel_action(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Действие отменено.")
    await call.answer()

@dp.callback_query(F.data == "cancel_delete")
async def cancel_delete(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Удаление отменено.")
    await call.answer()

@dp.message(AddGenre.waiting_name)
async def add_genre_process(message: Message, state: FSMContext):
    if add_genre(message.text.strip()):
        await message.answer(f"Жанр «{message.text}» добавлен ✅", reply_markup=admin_reply_kb)
    else:
        await message.answer("Такой жанр уже существует ❌", reply_markup=admin_reply_kb)
    await state.clear()

@dp.callback_query(AddMovie.choosing_genre, F.data.startswith("genre_"))
async def movie_choose_genre(call: CallbackQuery, state: FSMContext):
    genre_id = int(call.data.split("_")[1])
    await state.update_data(genre_id=genre_id)
    await state.set_state(AddMovie.waiting_title)
    await call.message.edit_text("Введи <b>название</b> фильма:", parse_mode="HTML")
    await call.answer()

@dp.message(AddMovie.waiting_title)
async def movie_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddMovie.waiting_description)
    await message.answer("Введи <b>описание</b> фильма:", parse_mode="HTML")

@dp.message(AddMovie.waiting_description)
async def movie_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddMovie.waiting_year)
    await message.answer("Введи <b>год</b> выхода:", parse_mode="HTML")

@dp.message(AddMovie.waiting_year)
async def movie_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(AddMovie.waiting_file)
    await message.answer("Отправь видео (mp4, mkv, avi и т.д.):")

@dp.message(AddMovie.waiting_file, F.video)
async def movie_file(message: Message, state: FSMContext):
    data = await state.get_data()
    add_movie(data["genre_id"], data["title"], data["description"], data["year"], message.video.file_id)
    await message.answer(f"Фильм «{data['title']}» добавлен ✅", reply_markup=admin_reply_kb)
    await state.clear()

@dp.message(StateFilter(None), F.text & ~F.text.startswith("/"))
async def text_search(message: Message):
    results = search_movies(message.text)
    if not results:
        await message.answer("Ничего не найдено.")
        return
    builder = InlineKeyboardBuilder()
    for mid, title, *_ in results:
        builder.button(text=title, callback_data=f"movie_{mid}")
    builder.adjust(1)
    await message.answer("Результаты поиска:", reply_markup=builder.as_markup())

async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())