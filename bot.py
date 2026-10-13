import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Hi! Your bot is online.\n\n"
        "Commands:\n"
        "/start - show this message\n"
        "/help - setup help\n"
        "/check - check integration setup"
    )


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "This is the starter bot. Before checking any account status, "
        "configure an official, authorized API and follow its terms. "
        "This starter does not query Swiggy or bypass anti-bot protections."
    )


@dp.message(Command("check"))
async def check_command(message: Message) -> None:
    await message.answer(
        "Bot is running, but no authorized status-checking API is configured yet."
    )


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing")
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
