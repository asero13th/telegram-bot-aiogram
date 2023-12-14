import asyncio
import logging
import sys
from os import getenv
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
import requests
from dotenv import load_dotenv
# Bot token can be obtained via https://t.me/BotFather

load_dotenv()
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
TOKEN = getenv("BOT_TOKEN")

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command

    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`

    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message(Command("hello_world"))
async def hello_world_handler(message: Message) -> None:
    """
    handler will forward hello world message

    """
    await message.answer("Hello world!")

@dp.message()
async def photo_handler(message: types.Message) -> None:
    """
    Handler will forward received photo back

    """
    bot = Bot("6784079632:AAHaC1fVGgfCXqqLLhul4Z0kiO1rFNwJCl0", parse_mode=ParseMode.HTML)
    if message.photo:
        file_path = bot.get_file(message.photo[-1].file_id)
        

        folder_path = "images"
        new_file_path = os.path.join(folder_path, f'photo_{message.from_user.first_name}_{message.photo[-1].file_unique_id}.jpg')
       
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path.file_path}') as resp:
                os.makedirs(folder_path, exist_ok=True)
                with open(new_file_path, 'wb') as f:
                    f.write(await resp.read())

        with open(new_file_path, 'rb') as photo:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={new_file_path: f},
                data={'apikey': 'K86055456288957'}
            )



async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())