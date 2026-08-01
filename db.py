import sqlite3
from typing import List, Optional, Tuple

DB_NAME = "cinema.db"

def _connect():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with _connect() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genre_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                year TEXT NOT NULL,
                file_id TEXT NOT NULL,
                FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            )
        """)
        con.commit()

def add_genre(name: str) -> bool:
    try:
        with _connect() as con:
            con.execute("INSERT INTO genres (name) VALUES (?)", (name,))
        return True
    except sqlite3.IntegrityError:
        return False

def delete_genre(genre_id: int):
    with _connect() as con:
        con.execute("DELETE FROM genres WHERE id = ?", (genre_id,))

def get_genres() -> List[Tuple[int, str]]:
    with _connect() as con:
        return con.execute("SELECT id, name FROM genres ORDER BY name").fetchall()

def add_movie(genre_id: int, title: str, description: str, year: str, file_id: str):
    with _connect() as con:
        con.execute(
            "INSERT INTO movies (genre_id, title, description, year, file_id) VALUES (?, ?, ?, ?, ?)",
            (genre_id, title, description, year, file_id)
        )

def delete_movie(movie_id: int):
    with _connect() as con:
        con.execute("DELETE FROM movies WHERE id = ?", (movie_id,))

def get_movies_by_genre(genre_id: int) -> List[Tuple]:
    with _connect() as con:
        return con.execute(
            "SELECT id, title, description, year, file_id FROM movies WHERE genre_id = ?",
            (genre_id,)
        ).fetchall()

def get_movie_by_id(movie_id: int) -> Optional[Tuple]:
    with _connect() as con:
        return con.execute(
            "SELECT id, title, description, year, file_id FROM movies WHERE id = ?",
            (movie_id,)
        ).fetchone()

def search_movies(query: str) -> List[Tuple]:
    with _connect() as con:
        return con.execute(
            """SELECT m.id, m.title, m.description, m.year, m.file_id 
               FROM movies m 
               JOIN genres g ON m.genre_id = g.id
               WHERE m.title LIKE ? OR g.name LIKE ?""",
            (f"%{query}%", f"%{query}%")
        ).fetchall()

def get_all_movies() -> List[Tuple]:
    with _connect() as con:
        return con.execute("SELECT id, title FROM movies ORDER BY title").fetchall()