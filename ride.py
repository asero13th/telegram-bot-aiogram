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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

load_dotenv()
TOKEN = getenv("RIDE_TOKEN")
form_router = Router()

class Form(StatesGroup):
    name = State()
    phone = State()
    role = State()
    current_location = State()
    destination = State()
    history = State()


@form_router.message(CommandStart())
async def message_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)

    await message.answer(
        "Hi there! What's your name?",
        reply_markup=ReplyKeyboardRemove(),
    )

@form_router.message(Form.name)
async def ask_phone(message: Message, state: FSMContext) -> None:
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
                    KeyboardButton(text="driver"),
                    KeyboardButton(text="passenger")
                ]
            ],resize_keyboard=True
        )
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

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())