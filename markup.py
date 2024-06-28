from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import channel


def show_channel():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn = InlineKeyboardButton(text=channel[0], url=channel[2])
    keyboard.insert(btn)
    btndone = InlineKeyboardButton(text="Check my subscription", callback_data="sub_ch_done")
    keyboard.insert(btndone)
    return keyboard


def profile_board():
    profile_board_mr = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Statistics 🚀", callback_data="statistic")
    btn2 = InlineKeyboardButton(text="Referrals 📞", callback_data="ref")
    btn3 = InlineKeyboardButton(text="Mining ⛏", callback_data="mine")
    profile_board_mr.add(btn1, btn2, btn3)
    return profile_board_mr


def ref():
    ref_board = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Refresh data 🔄", callback_data="ref_update")
    btn2 = InlineKeyboardButton(text="🔙 Back", callback_data="back")
    ref_board.add(btn1, btn2)
    return ref_board


def statis():
    statis_board = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Refresh data 🔄", callback_data="statis_update")
    btn2 = InlineKeyboardButton(text="🔙 Back", callback_data="back")
    statis_board.add(btn1, btn2)
    return statis_board


def back_btn():
    back_board = InlineKeyboardMarkup(row_width=3)
    btn2 = InlineKeyboardButton(text="🔙 Back", callback_data="back")
    back_board.add(btn2)
    return back_board


def mine_statis():
    mine_statis_board = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Mining statistics 📈", callback_data="mine_statis")
    btn2 = InlineKeyboardButton(text="Start mining ⛏", callback_data="mine_start")
    btn3 = InlineKeyboardButton(text="🔙 Back", callback_data="back")
    mine_statis_board.add(btn1, btn2, btn3)
    return mine_statis_board


def update_loc_p():
    loc_p_board = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Start mining ⛏", callback_data="update_loc_p")
    btn2 = InlineKeyboardButton(text="🔙 Go back to the menu", callback_data="back")
    loc_p_board.add(btn1, btn2)
    return loc_p_board
