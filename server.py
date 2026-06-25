import sqlite3
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Настройка CORS, чтобы твой GitHub Pages мог делать запросы к серверу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # На этапе разработки разрешаем запросы отовсюду
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect("wishlist.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishes (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            title TEXT,
            link TEXT,
            img TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Схема данных для добавления хотелки
class WishCreate(BaseModel):
    owner_id: int
    title: str = ""
    link: str = ""
    img: str = ""
    is_link: bool = False

@app.get("/api/wishes")
def get_wishes():
    conn = sqlite3.connect("wishlist.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, owner_id, title, link, img FROM wishes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"id": r[0], "ownerId": r[1], "title": r[2], "link": r[3], "img": r[4]}
        for r in rows
    ]

@app.post("/api/wishes")
def add_wish(wish: WishCreate):
    title = wish.title
    img = wish.img
    link = wish.link

    # Если добавляют по ссылке — включаем парсер
    if wish.is_link and link:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            res = requests.get(link, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Пытаемся вытащить стандартные мета-теги Open Graph (og:title, og:image)
            og_title = soup.find("meta", property="og:title")
            og_image = soup.find("meta", property="og:image")
            
            if og_title and og_title.get("content"):
                title = og_title["content"]
            else:
                # Если мета-тегов нет, берем просто тег <title> страницы
                title = soup.title.string if soup.title else f"Товар с сайта {link.split('/')[2]}"
                
            if og_image and og_image.get("content"):
                img = og_image["content"]
        except Exception as e:
            print(f"Ошибка парсинга ссылки: {e}")
            title = f"Товар по ссылке ({link.split('/')[2]})"

    conn = sqlite3.connect("wishlist.db")
    cursor = conn.cursor()
    wish_id = int(time.time() * 1000) # Генерация ID по текущему времени
    cursor.execute(
        "INSERT INTO wishes (id, owner_id, title, link, img) VALUES (?, ?, ?, ?, ?)",
        (wish_id, wish.owner_id, title, link, img)
    )
    conn.commit()
    conn.close()
    
    return {"status": "ok", "id": wish_id, "title": title, "img": img}

@app.delete("/api/wishes/{wish_id}")
def delete_wish(wish_id: int):
    conn = sqlite3.connect("wishlist.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishes WHERE id = ?", (wish_id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)