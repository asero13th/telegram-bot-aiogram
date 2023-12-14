"""
main function that will be called when the program starts"""
import asyncio
import logging
import sys
import sqlite3
import json
import random
from os import getenv
from aiogram import types
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv
from my_callback import MyCallback
from driver_role_handler import process_driver_role
from passanger_role_handler import process_passanger_role


load_dotenv()
TOKEN = getenv("RIDE_TOKEN")
form_router = Router()

if TOKEN is None:
    raise ValueError("Telegram token is not set")

class Form(StatesGroup):
    """
    This class represents a form with various states such as id, name, phone, role, etc.
    """
    id = State()
    fullname = State()
    phone = State()
    role = State()
    current_location = State()
    destination = State()
    history = State()
    date = State()


@form_router.message(CommandStart())
async def message_start(message: Message, state: FSMContext) -> None:
    """
    starting chat with the user
    """

    userid = message.chat.id
    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT fullname, phone, completed_rides FROM users WHERE user_id = ?', (userid,))
        result = cursor.fetchone()

        if result:
            menu = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='🚘 Book Ride', callback_data=MyCallback(name="ride", id="4").pack()),
                    InlineKeyboardButton(text='🔁 Driver Matching', callback_data=MyCallback(name="match", id="5").pack())
                ],
                 [
                    InlineKeyboardButton(text='⭐️ Rate Driver', callback_data=MyCallback(name="rate", id="6").pack()),
                    InlineKeyboardButton(text='🧾 History', callback_data=MyCallback(name="history", id="7").pack())]
                  ,[
                     InlineKeyboardButton(text='⚙️ Profile', callback_data=MyCallback(name="profile", id="8").pack())
                   ],
            ])
            await message.answer(f'Welcome back {result[0]}', reply_markup=menu)
        else:
            await state.set_state(Form.fullname)
            await message.answer(
                "Hi there! What's your name?",
                reply_markup=ReplyKeyboardRemove(),
            )
    except Exception as e:
        #handle valueError exception here
        print(f'error occured at {e}')
    finally:
        conn.close()


@form_router.message(Form.fullname)
async def ask_phone(message: Message, state: FSMContext) -> None:
    """
    a method to as phone number from the user
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
    """
    a method to ask role of the user
    """
    await state.update_data(phone = message.contact.phone_number)
    await state.set_state(Form.role)

    role = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🚘 Driver', callback_data=MyCallback(name="driver", id="1").pack()),
            InlineKeyboardButton(text='👤 Passenger', callback_data=MyCallback(name='passanger', id="2").pack())
        ]
    ])
    await message.answer(
        "enter your role",
        reply_markup=role
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

@form_router.callback_query(MyCallback.filter(F.name == "driver"))
async def callback_process_driver_role(query: CallbackQuery, callback_data: MyCallback, state: FSMContext):
    """
    a callback function that procss the driver role if the role button is pressed"""

    await process_driver_role(query, callback_data, state)

@form_router.callback_query(MyCallback.filter(F.name == "passanger"))
async def callback_process_passanger_role(query: CallbackQuery, callback_data: MyCallback, state: FSMContext):
    """
    a callback function that process the passanger role if the passanger button is pressed"""

    await process_passanger_role(query, callback_data, state)


@form_router.callback_query(MyCallback.filter(F.name == "home"))
async def process_home(query: types.CallbackQuery, callback_data: MyCallback) -> None:
    """
    this function will be called if home button is pressed"""
    await query.message.delete()
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🚘 Book Ride', callback_data=MyCallback(name="ride", id="4").pack()),
    InlineKeyboardButton(text='🔁 Driver Matching', callback_data=MyCallback(name="match", id="5").pack())],
    [InlineKeyboardButton(text='⭐️ Rate Driver', callback_data=MyCallback(name="rate", id="6").pack()),
    InlineKeyboardButton(text='🧾 History', callback_data=MyCallback(name="history", id="7").pack())],
    [InlineKeyboardButton(text='⚙️ Profile', callback_data=MyCallback(name="profile", id="8").pack())],], )
    await query.message.answer(f"{hbold('Welcome to Ride Healing Bot 🚖')}!\n\nSteer your ride! Where would you like to go?😎\nSelect from features ..  ", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "ride"))
async def process_ride(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    await state.set_state(Form.current_location)
    await query.message.answer(
        "please share your Location",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Share Location", request_location=True)
                ]
            ],resize_keyboard=True
        ) 
        )

@form_router.message(Form.current_location)
async def process_current_location(message: types.Message, state: FSMContext) -> None:

    data = await state.get_data()
    currentlocation = data.get("current_location",[])
    currentlocation.append(message.location)

    await state.update_data(current_location = currentlocation)
    await state.set_state(Form.destination)
    await message.answer(
        "please share your destination",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Share Location", request_location=True)
                ]
            ],resize_keyboard=True
        ) 
        )

@form_router.message(Form.destination)
async def process_destination(message: types.Message, state: FSMContext) -> None:

    data = await state.get_data()
    dest = data.get("destination",[])
    dest.append(message.location)

    userid = message.chat.id
    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT fullname, phone, completed_rides FROM users WHERE user_id = ?', (userid,))
        result = cursor.fetchone()

        if result:
            fullname, phone,curr_completed_rides_str = result
            current_completed_rides = json.loads(curr_completed_rides_str)
            print("Full Name:", fullname)
            print("Phone Number:", phone)
            print("Curr Location:", data.get("current_location")   )
            print("Destination:", data.get("destination")   )
            print("Current Completed Rides:", current_completed_rides)

        else:
            print("User not found.")
    except Exception as e:
        #handle valueError exception here
        print(f'error occured at {e}')
    finally:
        conn.close()
    
    curr_location = data.get("current_location")
    curr_destination = data.get("destination")
    ride_info = [curr_location, curr_destination]
    current_completed_rides.append(ride_info)

    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET completed_rides = ? WHERE user_id = ?', (json.dumps(current_completed_rides), userid))
        conn.commit()

    except Exception as e:
        #handle valueError exception here
        print(f'error occured at {e}')
    finally:
        conn.close()
    
    # Fake progress bar
    progress_message = await message.answer("Calculating time... [                      ]")

    for i in range(1, 11):
        await asyncio.sleep(0.5)  # Simulate some processing time
        bar = "[" + "▬" * i + " " * (10 - i) + "]"
        await progress_message.edit_text(f"⏳Calculating time. \nPlease wait...\n {bar}")
    
    estimated_time = random.randint(5, 30)
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]])
    await progress_message.edit_text(f"⏰Estimated arrival time from {message.text} is {hbold(estimated_time)} minutes. \n Your Driver will arrive soon.", reply_markup=menu )
    
@form_router.callback_query(MyCallback.filter(F.name == "match"))
async def process_match(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]]
            )
    await query.message.answer("✅ Notification is on.\nYou will be notified when booking ride", reply_markup=menu)

@form_router.callback_query(MyCallback.filter(F.name == "rate"))
async def process_rate(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext):
    userid = query.message.chat.id
    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (userid,))
        result = cursor.fetchone()

        if not result:
            query.message.answer("You are not registered")
        elif result[0] == "driver":
            cursor.execute('SELECT user_id, fullname FROM users WHERE role = ?', ("driver",))
            passangers = cursor.fetchall()

            if not passangers:
                query.message.answer('no passangers Found')
            else:
                menu = InlineKeyboardMarkup(
                    inline_keyboard=[
                       [InlineKeyboardButton(text = f'rate {passanger[1]}', callback_data=MyCallback(name="rate_passanger", id=f'{passanger[0]}')) ] for passanger in passangers
                    ]
                )
        elif result[0] == "passanger":
            cursor.execute('SELECT user_id, fullname FROM users WHERE role = ?', ("driver",))
            drivers = cursor.fetchall()

            if not drivers:
                query.message.answer('no drivers Found')
            else:
                menu = InlineKeyboardMarkup(
                    inline_keyboard=[
                       [InlineKeyboardButton(text = f'rate {driver[1]}', callback_data=MyCallback(name="rate_driver", id=f'{driver[0]}')) ] for driver in drivers
                    ]
                )
        else:
            query.message.answer("You are not registered")
    except Exception as e:
        #handle valueError exception here
        print(f'error occured at {e}')

    finally:
        conn.close()
        

@form_router.callback_query(MyCallback.filter(F.name == "rate_passanger"))
async def process_rate_passanger(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    await query.message.answer("please rate the driver")
    menu = InlineKeyboardMarkup(inline_keyboard=[
                # stars
                    [  InlineKeyboardButton(text='⭐️', callback_data=MyCallback(name="star", id="1").pack())],
                    [  InlineKeyboardButton(text='⭐️⭐️', callback_data=MyCallback(name="star", id="2").pack())],
                    [  InlineKeyboardButton(text='⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="3").pack())],
                    [  InlineKeyboardButton(text='⭐️⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="4").pack())],
                    [  InlineKeyboardButton(text='⭐️⭐️⭐️⭐️⭐️', callback_data=MyCallback(name="star", id="5").pack())],
                
            ])

@form_router.callback_query(MyCallback.filter(F.name == "star"))
async def process_star(query: types.CallbackQuery, callback_data: MyCallback, state: FSMContext) -> None:
    menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Back', callback_data=MyCallback(name="home", id="3").pack())]])
    await query.message.answer("WE recorded your rating, \nthank you for rating", reply_markup=menu)


async def main():
    """
    main function"""
    bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())