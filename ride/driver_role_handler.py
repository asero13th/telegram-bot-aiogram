"""
imoort sqlite3"""
import sqlite3
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.markdown import hbold
from my_callback import MyCallback


async def process_driver_role(query, callback_data, state):
    """
    this function process drivers role
    """
    state.update_data(role=callback_data.name)
    await query.message.answer("successfully registered!")

    user_data = await state.get_data()
    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()

    user_id = query.message.chat.id
    username = user_data.get('fullname')
    phone = user_data.get('phone')
    role = 'driver'
    date = user_data.get('date')

    cursor.execute(
        '''

        INSERT INTO users (user_id, username, state, fullname, phone, role, history, registration_date, rating, completed_rides) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)
        ''',(user_id, username, 'state1',username, phone, role, "", date,0,"[]")
    )

    conn.commit()
    conn.close()

    await query.message.delete()
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
    await query.message.answer(f"{hbold('Welcome to Ride Healing Bot 🚖')}!\n\nSteer your ride! Where would you like to go?😎\nSelect from features ..", reply_markup=menu)
