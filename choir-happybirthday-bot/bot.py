import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from html import escape

from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


load_dotenv()
TOKEN = getenv("BOT_TOKEN")
form_router = Router()

class Form(StatesGroup):
    full_name = State()
    phone = State()
    role = State()
    batch = State()
    sex = State()
    voice_group = State()
    church = State()
    city = State()
    birthday = State()
    department = State()
   


@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:

    """
    This handler receives messages with `/start` command
    
    """
    await state.set_state(Form.full_name)
    await message.answer(
        "Hi there! What's your name?",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Command("Cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def command_cancel(message: Message, state: FSMContext) -> None:
    """
    allow the user to cancel

    """
    current_state = await state.get_state()
    if current_state is None:
        return
    
    logging.info("canceling info from %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    
    )

@form_router.message(Form.full_name)
async def ask_phone(message: Message, state: FSMContext) -> None:
    """
    ask the user to provide phone

    """
    await state.update_data(name = message.text)
    await state.set_state(Form.phone)
    await message.answer(
       "please share you phone number",
       reply_markup=ReplyKeyboardMarkup(
           keyboard = [
               [
                   KeyboardButton(text="Share Phone", request_contact=True)
               ]
           ],resize_keyboard=True
       )
    )
@form_router.message(Form.phone)
async def ask_role(message: Message, state: FSMContext) -> None:
    await state.update_data(phone = message.contact.phone_number)
    await state.set_state(Form.role)
    await message.answer(
        "enter your role",
        reply_markup=ReplyKeyboardMarkup(
            keyboard = [
                [
                    KeyboardButton(text="muician"),
                    KeyboardButton(text="vocal")
                ]
            ],resize_keyboard=True
        )
    )

@form_router.message(Form.role)
async def ask_batch(message: Message, state: FSMContext) -> None:
    await state.update_data(role = message.text)
    await state.set_state(Form.batch)
    await message.answer(
        "enter your batch",
        reply_markup=ReplyKeyboardRemove()
    )

@form_router.message(Form.batch)
async def ask_sex(message: Message, state: FSMContext) -> None:
    await state.update_data(batch = message.text)
    await state.set_state(Form.sex)
    await message.answer(
        "enter your role",
        reply_markup=ReplyKeyboardMarkup(
            keyboard = [
                [
                    KeyboardButton(text="male"),
                    KeyboardButton(text="female")
                ]
            ],resize_keyboard=True
        )
    )

@form_router.message(Form.sex)
async def ask_voice_group(message: Message, state: FSMContext) -> None:
    await state.update_data(sex = message.text)
    await state.set_state(Form.voice_group)
    await message.answer(
        "enter your voice group",
        reply_markup=ReplyKeyboardMarkup(
            keyboard = [
                [
                    KeyboardButton(text="Tenor"),
                    KeyboardButton(text="Bass"),
                    KeyboardButton(text="Alto"),
                    KeyboardButton(text="Soprano"),

                ]
            ],resize_keyboard=True
        )
    )
@form_router.message(Form.voice_group)
async def ask_church(message: Message, state: FSMContext) -> None:
    """
    ask the user to provide church
    """
    await state.update_data(voice_group = message.text)
    await state.set_state(Form.church)
    await message.answer(
        "enter your church",
        reply_markup=ReplyKeyboardRemove()
    )
@form_router.message(Form.church)

async def ask_city(message: Message, state: FSMContext) -> None:
    """
    ask the user to provide city
    """
    await state.update_data(church = message.text)
    await state.set_state(Form.city)
    await message.answer(
        "enter your city",
        reply_markup=ReplyKeyboardRemove()
    )
@form_router.message(Form.city)
async def ask_birthday(message: Message, state: FSMContext) -> None:
    """
    ask the user to provide birthday
    """
    await state.update_data(city = message.text)
    await state.set_state(Form.birthday)
    await message.answer(
        "enter your birthday",
        reply_markup=ReplyKeyboardRemove()
    )


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())