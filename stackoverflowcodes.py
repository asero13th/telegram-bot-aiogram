
import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from dotenv import load_dotenv
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, types, F, Router


load_dotenv()
TOKEN = getenv("RIDE_TOKEN")
form_router = Router()

import asyncio
import logging



logging.basicConfig(level=logging.INFO)
bot = Bot(token="RIDE_TOKEN")
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    photo_url = 'YOUR_IMAGE_URL'

    await message.answer_photo(photo_url,
                               caption="Hello there! Here's a welcome message with an image. Good luck!")

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Share Contact",
        callback_data="share_contact",
        request_contact=True),
    )

    await message.answer(
        "Please share your contact with us:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "share_contact")
async def share_contact(callback: types.CallbackQuery):
    user = callback.from_user
    print("phone", callback.message.contact)
    await bot.send_message(user.id, f"User: {user}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
