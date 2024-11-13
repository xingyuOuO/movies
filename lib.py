import sqlite3
import json
import os
from typing import Optional

DB_PATH = "movies.db"
JSON_IN_PATH = "movies.json"
JSON_OUT_PATH = "exported.json"

def connect_db(db_path: str) -> sqlite3.Connection:
    """連接至 SQLite 資料庫"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 以字典格式回傳查詢結果
    return conn

def create_table(conn: sqlite3.Connection):
    """建立 movies 資料表"""
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    director TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    rating REAL CHECK(rating >= 1.0 AND rating <= 10.0)
                );
            """)
        print("資料表已建立（若不存在）")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")

def import_movies(conn: sqlite3.Connection, json_path: str):
    """從 JSON 檔案匯入電影資料"""
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            movies = json.load(file)
            with conn:
                conn.executemany("""
                    INSERT INTO movies (title, director, genre, year, rating)
                    VALUES (:title, :director, :genre, :year, :rating)
                """, movies)
            print("電影已匯入")
    except FileNotFoundError:
        print("找不到檔案...")
    except json.JSONDecodeError:
        print("無法解析 JSON 檔案")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")

def search_movies(conn: sqlite3.Connection):
    """查詢電影資料"""
    all_movies = input("查詢全部電影嗎？(y/n): ").strip().lower() == 'y'
    if all_movies:
        cursor = conn.execute("SELECT * FROM movies")
    else:
        movie_title = input("請輸入電影名稱: ")
        cursor = conn.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))

    print(f"{'電影名稱':{chr(12288)}<10}{'導演':{chr(12288)}<12}{'類型':{chr(12288)}<8}{'上映年份':<6}{'評分'}")
    print("-" * 50)
    for row in cursor:
        print(f"{row['title']:{chr(12288)}<10}{row['director']:{chr(12288)}<12}{row['genre']:{chr(12288)}<8}{row['year']:<6}{row['rating']}")

def add_movie(conn: sqlite3.Connection):
    """新增電影資料"""
    title = input("電影名稱: ")
    director = input("導演: ")
    genre = input("類型: ")
    year = input("上映年份: ")
    rating = input("評分 (1.0 - 10.0): ")

    try:
        with conn:
            conn.execute("""
                INSERT INTO movies (title, director, genre, year, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (title, director, genre, int(year), float(rating)))
        print("電影已新增")
    except ValueError:
        print("輸入格式有誤，請檢查年份或評分是否為數字")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")

def modify_movie(conn: sqlite3.Connection):
    """修改電影資料"""
    title = input("請輸入要修改的電影名稱: ")
    cursor = conn.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{title}%',))
    movies = cursor.fetchall()
    if not movies:
        print("查無此電影")
        return

    for row in movies:
        print(f"電影名稱: {row['title']}, 導演: {row['director']}, 類型: {row['genre']}, 上映年份: {row['year']}, 評分: {row['rating']}")

    new_title = input("請輸入新的電影名稱 (若不修改請直接按 Enter): ")
    new_director = input("請輸入新的導演 (若不修改請直接按 Enter): ")
    new_genre = input("請輸入新的類型 (若不修改請直接按 Enter): ")
    new_year = input("請輸入新的上映年份 (若不修改請直接按 Enter): ")
    new_rating = input("請輸入新的評分 (1.0 - 10.0) (若不修改請直接按 Enter): ")

    try:
        with conn:
            conn.execute("""
                UPDATE movies
                SET title = COALESCE(NULLIF(?, ''), title),
                    director = COALESCE(NULLIF(?, ''), director),
                    genre = COALESCE(NULLIF(?, ''), genre),
                    year = COALESCE(NULLIF(CAST(? AS INTEGER), ''), year),
                    rating = COALESCE(NULLIF(CAST(? AS REAL), ''), rating)
                WHERE title LIKE ?
            """, (new_title, new_director, new_genre, new_year, new_rating, f'%{title}%'))
        print("資料已修改")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")

def delete_movies(conn: sqlite3.Connection):
    """刪除電影資料"""
    all_movies = input("刪除全部電影嗎？(y/n): ").strip().lower() == 'y'
    if all_movies:
        confirm = input("是否要刪除所有電影資料？(y/n): ")
        if confirm == 'y':
            with conn:
                conn.execute("DELETE FROM movies")
            print("所有電影已刪除")
    else:
        title = input("請輸入要刪除的電影名稱: ")
        with conn:
            conn.execute("DELETE FROM movies WHERE title LIKE ?", (f'%{title}%',))
        print("電影已刪除")

def export_movies(conn: sqlite3.Connection, json_out_path: str):
    """匯出電影資料至 JSON 檔案"""
    all_movies = input("匯出全部電影嗎？(y/n): ").strip().lower() == 'y'
    if all_movies:
        cursor = conn.execute("SELECT * FROM movies")
    else:
        title = input("請輸入要匯出的電影名稱: ")
        cursor = conn.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{title}%',))

    movies = [dict(row) for row in cursor]
    try:
        with open(json_out_path, 'w', encoding='utf-8') as file:
            json.dump(movies, file, ensure_ascii=False, indent=4)
        print("電影資料已匯出至 exported.json")
    except IOError:
        print("無法寫入檔案")
