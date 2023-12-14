""""
a module that process passanger """
import sqlite3
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from aiogram.utils.markdown import hbold
from my_callback import MyCallback

async def process_passanger_role(query, callback_data, state):
    """
    a function that process passanger role"""
    await state.update_data(role = callback_data.name)
    await query.message.answer("successfully registered!")

    user_data  = await state.get_data()
    conn = sqlite3.connect('ride/users.db')
    cursor = conn.cursor()


    cursor.execute('''
        INSERT INTO users (user_id, username, state, fullname, phone, role, history, registration_date, rating, completed_rides) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)
        ''',(query.message.chat.id, user_data.get('fullname'), 'state1',user_data.get('fullname'), user_data.get('phone'), 'passanger', "", user_data.get('date'),0,"[]")
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
            InlineKeyboardButton(text='🧾 History', callback_data=MyCallback(name="history", id="7").pack())
        ],
        [
            InlineKeyboardButton(text='⚙️ Profile', callback_data=MyCallback(name="profile", id="8").pack())
        ]
    ])

    await query.message.answer(f"{hbold('Welcome to Ride Healing Bot 🚖')}!\n\nSteer your ride! Where would you like to go?😎\nSelect from features ..", reply_markup=menu)