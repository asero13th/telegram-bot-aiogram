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
    name = State()
    email = State()
    age = State()
    sex = State()
    country = State()

@form_router.message(CommandStart())
async def message_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
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
@form_router.message(Form.name)
async def ask_email(message: Message, state: FSMContext) -> None:
    """
    ask the user to provide email

    """
    await state.update_data(name = message.text)
    await state.set_state(Form.email)
    await message.answer(
        "enter your email, please",
        reply_markup=ReplyKeyboardRemove(),
    )
@form_router.message(Form.email)
async def ask_age(message: Message, state: FSMContext) -> None:
    """
    ask the user for age
    """
    await state.update_data(email = message.text)
    await state.set_state(Form.age)
    await message.answer(
        "enter your age",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.age)
async def ask_gender(message: Message, state: FSMContext) -> None:
    """
    ask the user for sex
    """
    await state.update_data(age = message.text)
    await state.set_state(Form.sex)
    await message.answer(
        "sex",
         reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="male"),
                    KeyboardButton(text="female"),
                ]
            ],
            resize_keyboard=True,
        ),
    )

@form_router.message(Form.sex)
async def ask_country(message: Message, state: FSMContext) -> None:
    """
    ask for country
    """
    await state.update_data(sex=message.text.casefold())  # Fix the casefold() typo
    await state.set_state(Form.country)
    await message.answer(
        "enter your country",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.country)
async def show_summary(message: Message, state: FSMContext) -> None:
    """
    show summary
    """
    await state.update_data(country=message.text)
    data = await state.get_data()
    await state.clear()
    await message.answer(
        "Summary:",
        f"Name: {escape(data.get('name'))}\n"
        f"Email: {escape(data.get('email'))}\n"
        f"Age: {escape(data.get('age'))}\n"
        f"Sex: {escape(data.get('sex'))}\n"
        f"Country: {escape(data.get('country'))}",
        reply_markup=ReplyKeyboardRemove(),
    )

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
