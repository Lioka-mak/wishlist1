import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ВАЖНО: Вставь сюда токен, который дал BotFather
BOT_TOKEN = "8992437289:AAGxa13bGENVqBL3_Df_mqW6qKhGfKsPClE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    # Создаем кнопку для запуска приложения
    builder = ReplyKeyboardBuilder()
    
    # Пока приложение не на сервере, мы дадим ссылку на тестовую веб-страницу.
    # Позже мы заменим ее на ссылку твоего сайта.
    builder.button(
        text="ХоТеЛкИ", 
        web_app=WebAppInfo(url="https://lioka-mak.github.io/wishlist1/") # Пока заглушка
    )
    
    await message.answer(
        "Привет! Я бот для ваших хотелок. Жми кнопку ниже, чтобы открыть вишлист хотелок!",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())