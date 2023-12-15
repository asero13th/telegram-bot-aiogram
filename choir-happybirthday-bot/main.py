import asyncio
import logging
import sys
import sqlite3
from os import getenv
from typing import Any, Dict
from aiogram import types
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from dotenv import load_dotenv
from my_callback import MyCallback




load_dotenv()
TOKEN = getenv("BOT_TOKEN")
form_router = Router()

class Form(StatesGroup):
    """
    This class represents a form with various states such as id, name, phone, role, etc.
    """
    id = State()
    full_name = State()
    phone = State()
    batch = State()
    sex = State()
    voice_group = State()
    church = State()
    city = State()
    birthday = State()
    department = State()
    attendance = State()
    care_children = State()
    care_parent = State()
    feedback = State()
    prayer_request = State()
    role = State()
    date = State()
    history = State()
    technical_result = State()
    
   
@form_router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    """
    This function handles the /start command.
    """
    userid = message.chat.id
    conn = sqlite3.connect('choir-happybirthday-bot/users.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT fullname, phone, role,  FROM users WHERE user_id = ?", (userid,))
        user = cursor.fetchone()
        if user:
            if user[2] == "leader":
                menu = "somthing"
            elif user[2] == "care":
                menu = "somthing"
            elif user[2] == "zema":
                menu = "somthing"
            elif user[2] == "musician":
                menu = "somthing"
            elif user[2] == "pledge":
                menu = "somthing"
            elif user[2] == "member":
                menu = "somthing"
            else:
                menu = "somthing"
        
        else:
            menu = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='▶️ Register', callback_data=MyCallback(name="register", id="1").pack()),
                    InlineKeyboardButton(text='🚮Team info', callback_data=MyCallback(name="get_team_info", id="2").pack()),
                   
                ],[
                    InlineKeyboardButton(text='❔Ask Information', callback_data=MyCallback(name="ask_team_info", id="3").pack()),
                ]
            ])


    except Exception as e:
        logging.error(e)
        await message.answer("An error occured! restart please")
 
@form_router.callback_query(MyCallback.filter(F.name =="register"))
async def register(query: CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    """
    This function handles the register callback.
    """
    await state.set_state("full_name")
    await query.message.answer("Please enter your full name", reply_markup=ReplyKeyboardRemove())

@form_router.message(Form.full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    """
    This function handles the full name state.
    """
    full_name = message.text
    await state.set_state("phone")
    await state.update_data(full_name=full_name)
    await message.answer("Please enter your phone number", 
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="Share phone number", request_contact=True)]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                )
@form_router.message(Form.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """
    This function handles the batch state.
    """
    phone = message.contact.phone_number
    await state.update_data(phone = phone)
    menu = InlineKeyboardMarkup(inline_keyboard=[

        [InlineKeyboardButton(text=f'{num}', callback_data=MyCallback(name=f'{num}', id="100").pack()),] for num in range(2011, 2017)
    ])
    await message.answer("what is you batch", reply_markup=menu)
@form_router.callback_query(MyCallback.filter(F.id == "100"))
async def process_batch(query: CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    """
    This function handles the batch callback.
    """
    batch = callback_data.name
    await state.set_state("voice_group")
    await state.update_data(batch = batch)
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Alto', callback_data=MyCallback(name="alto", id="101").pack()),
            InlineKeyboardButton(text='Soprano', callback_data=MyCallback(name="soprano", id="101").pack()),
         ],
        [
            InlineKeyboardButton(text='Tenor', callback_data=MyCallback(name="tenor", id="101").pack()),
            InlineKeyboardButton(text='Soprano', callback_data=MyCallback(name="bass", id="101").pack()),
         ],
    ]
    )

    await query.message.answer("what is you voice group?", reply_markup=menu)
async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())