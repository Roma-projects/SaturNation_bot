import config
from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import aioschedule as schedule
from aiobdsqllite import Database
from asynparser import parse as saturn_parser
from asynparser import course_usdt as c_usdt
from tonconnect.connector import AsyncConnector
import asyncio
import markup as mr
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiosqlite
import tempfile
import os
import sqlite3


USER_CHAT_ID = '5017793187'
DB_PATH = '/root/SaturNation_bot/Saturn_user.db'


async def send_database_dump():
    # Создаем соединение с базой данных
    async with aiosqlite.connect(DB_PATH) as db:
        # Создаем временный файл для хранения дампа
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_name = temp_file.name
        temp_file.close()

        # Открываем новое соединение с временным файлом
        backup_con = sqlite3.connect(temp_file_name)
        # Выполняем бэкап во временный файл
        await db.backup(backup_con)
        backup_con.close()

        # Отправляем дамп как документ в Telegram
        with open(temp_file_name, 'rb') as f:
            await bot.send_document(USER_CHAT_ID, ('database_dump.db', f.read()))

        # Удаляем временный файл
        os.remove(temp_file_name)



storage = MemoryStorage()

bot = Bot(token=config.BOT_TOKEN)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

dp = Dispatcher(bot, storage=storage, loop=loop)

db = Database("Saturn_user.db")


class UserState(StatesGroup):
    refferer_id = State()


async def check_sub(channels, user_id):
    chat_member = await bot.get_chat_member(chat_id = channels[1] ,user_id = user_id)
    if chat_member['status'] == 'left':
        return False
    else:
        return True


@dp.message_handler(commands=['start'], state="*")
async def start(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        await message.delete()
        if await check_sub(config.channel, message.from_user.id):
            await bot.send_message(message.from_user.id, text="The bot has started working")
            await bot.send_message(message.from_user.id, text=config.profile_message, reply_markup=mr.profile_board())
            start_command = message.text
            if await db.user_not_exists(message.from_user.id):
                refferer_id = str(start_command[7:])
                await state.update_data(refferer_id=refferer_id)
                if refferer_id and refferer_id != str(message.from_user.id):
                    await db.add_user(message.from_user.id, refferer_id)
                else:
                    await db.add_user(message.from_user.id)
        else:
            await bot.send_message(message.from_user.id, config.notsub_message, reply_markup=mr.show_channel())


@dp.callback_query_handler(text="sub_ch_done", state=UserState.refferer_id)
async def sub_ch_done(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    if await check_sub(config.channel, callback_query.from_user.id):
        if await db.user_not_exists(callback_query.from_user.id):
            user_data = await state.get_data()
            refferer_id = user_data.get('refferer_id', '')
            if refferer_id and refferer_id != str(callback_query.from_user.id):
                await db.add_user(callback_query.from_user.id, refferer_id)
            else:
                await db.add_user(callback_query.from_user.id)

        await bot.send_message(callback_query.from_user.id, text=config.profile_message, reply_markup=mr.profile_board())
    else:
        await bot.send_message(callback_query.from_user.id, config.notsub_message, reply_markup=mr.show_channel())


@dp.callback_query_handler(text="ref")
async def ref(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    ref_count = await db.ref_counter(callback_query.from_user.id)
    ref_text = f"Your referral link:  `https://t.me/SaturNation_bot?start={callback_query.from_user.id}`\n" \
               f"Number of referrals: {ref_count}"
    await bot.send_message(callback_query.from_user.id, text=ref_text, parse_mode='Markdown', reply_markup=mr.ref())


@dp.callback_query_handler(text="ref_update")
async def ref_update(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    m = await bot.send_message(callback_query.from_user.id, text="The data has been updated, do not spam!")
    await asyncio.sleep(3)
    await bot.delete_message(callback_query.from_user.id, m.message_id)
    ref_count = await db.ref_counter(callback_query.from_user.id)
    ref_text = f"Your referral link:  `https://t.me/SaturNation_bot?start={callback_query.from_user.id}`\n" \
               f"Number of referrals: {ref_count}"
    await bot.send_message(callback_query.from_user.id, text=ref_text, parse_mode='Markdown', reply_markup=mr.ref())


@dp.callback_query_handler(text="back")
async def back(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, text=config.profile_message, reply_markup=mr.profile_board())


@dp.callback_query_handler(text="statistic")
async def statistic(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    ref_count = await db.ref_counter(callback_query.from_user.id)
    saturn_balance = await db.get_saturn_balance(callback_query.from_user.id)
    mine_lvl = await db.get_mine_lvl(callback_query.from_user.id)
    user_rank = await db.check_user_rank(callback_query.from_user.id)

    statis_text = f"🪐 Your stats 🪐 \n\n" \
                  f"Number of referrals: {ref_count} 📞\n" \
                  f"Balance: {saturn_balance} Saturn 💸\n" \
                  f"The level of mining pumping: {mine_lvl} 📈\n" \
                  f"Place in the top: {user_rank} 🏆"
    await bot.send_message(callback_query.from_user.id, text=statis_text, reply_markup=mr.statis())


@dp.callback_query_handler(text="mine")
async def mine(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    wallet_connected = await db.is_wallet_connected(callback_query.from_user.id)
    if not wallet_connected:
        connector = AsyncConnector('https://tonclick.online/ton-connect.json', use_tonapi=True, tonapi_token=None)
        url = await connector.connect('tonkeeper', 'test')
        connect_board = InlineKeyboardMarkup(row_width=3)
        btn1 = InlineKeyboardButton(text="Connect", url=url)
        connect_board.add(btn1)
        msg = await bot.send_message(callback_query.from_user.id, text=config.wallet_message, parse_mode='Markdown', reply_markup=connect_board)
        try:
            address = await connector.get_address()
            await db.save_wallet_address(callback_query.from_user.id, address)
            await asyncio.sleep(1)
            wallet_connected = await db.is_wallet_connected(callback_query.from_user.id)
            await asyncio.sleep(1)
            if wallet_connected:
                await bot.delete_message(callback_query.from_user.id, msg.message_id)
                await bot.send_message(callback_query.from_user.id, text="✨ You have successfully connected, go back to the main menu and click the mining button again ✨", reply_markup=mr.back_btn())
                await db.update_to_true_status_one(callback_query.from_user.id)
                await db.update_start_loc_p(callback_query.from_user.id)
        except AttributeError:
            await bot.delete_message(callback_query.from_user.id, msg.message_id)
            await bot.send_message(callback_query.from_user.id, text="Connection error try again",
                                   reply_markup=mr.back_btn())
        except TimeoutError:
            await bot.delete_message(callback_query.from_user.id, msg.message_id)
            await bot.send_message(callback_query.from_user.id, text="Connection timeout exceeded",
                                   reply_markup=mr.back_btn())
        except Exception:
            await bot.delete_message(callback_query.from_user.id, msg.message_id)
            await bot.send_message(callback_query.from_user.id, text="Try to connect again",
                                   reply_markup=mr.back_btn())
    else:
        await bot.send_message(callback_query.from_user.id, text="✨ You are successfully connected to the mining system. Go to the statistics to find out more ✨", reply_markup=mr.mine_statis())


@dp.callback_query_handler(text="mine_statis")
async def mine_statis(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    address = await db.get_wallet_address(callback_query.from_user.id)
    balance = await saturn_parser(address)
    await db.update_saturn_balance(callback_query.from_user.id, balance)
    if balance is not False:
        course = await c_usdt()
        balance_in_usdt = course * balance
        await db.update_saturn_balance_in_usdt(callback_query.from_user.id, balance_in_usdt)
    else:
        balance_in_usdt = 0

    mine_lvl = await db.get_mine_lvl(callback_query.from_user.id)
    global_part = await db.get_global_part(callback_query.from_user.id)
    local_part = await db.get_local_part(callback_query.from_user.id)

    await bot.send_message(callback_query.from_user.id, text=f"🪐 Your stats 🪐 \n\n" \
                                                             f"Balance in usdt: {balance_in_usdt:.2f} 🤑\n" \
                                                             f"Balance in Saturn: {balance:.2f} 💸\n" \
                                                             f"The level of mining pumping: {mine_lvl} 📈\n" \
                                                             f"Global_part: {global_part}% 😎\n" \
                                                             f"Local_part: {local_part}% 🦾", reply_markup=mr.back_btn())


@dp.callback_query_handler(text="mine_start")
async def mine_start(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    address = await db.get_wallet_address(callback_query.from_user.id)
    balance = await saturn_parser(address)
    await db.update_saturn_balance(callback_query.from_user.id, balance)

    course = await c_usdt()
    balance_in_usdt = course * balance
    await db.update_saturn_balance_in_usdt(callback_query.from_user.id, balance_in_usdt)

    status = await db.update_or_check_status(callback_query.from_user.id)
    if status == 1:
        await bot.send_message(callback_query.from_user.id, text=config.mining_message, parse_mode='Markdown', reply_markup=mr.update_loc_p())
    else:
        await bot.send_message(callback_query.from_user.id, text="Your farming status is still active, come back later.", reply_markup=mr.back_btn())


@dp.callback_query_handler(text="statis_update")
async def status_update(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    m = await bot.send_message(callback_query.from_user.id, text="The data has been updated, do not spam!")
    await asyncio.sleep(3)
    await bot.delete_message(callback_query.from_user.id, m.message_id)
    ref_count = await db.ref_counter(callback_query.from_user.id)
    saturn_balance = await db.get_saturn_balance(callback_query.from_user.id)
    mine_lvl = await db.get_mine_lvl(callback_query.from_user.id)
    user_rank = await db.check_user_rank(callback_query.from_user.id)

    statis_text = f"🪐 Your stats 🪐 \n\n" \
                  f"Number of referrals: {ref_count} 📞\n" \
                  f"Balance: {saturn_balance} Saturn 💸\n" \
                  f"The level of mining pumping: {mine_lvl} 📈\n" \
                  f"Place in the top: {user_rank} 🏆"
    await bot.send_message(callback_query.from_user.id, text=statis_text, reply_markup=mr.statis())


@dp.callback_query_handler(text="update_loc_p")
async def update_local_part(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, text="You have started mining, the timer is running", reply_markup=mr.back_btn())
    await db.update_local_part(callback_query.from_user.id)
    await db.update_to_zero_status(callback_query.from_user.id)


@dp.message_handler()
async def echo(message: types.Message):
    await message.delete()


async def daily_scheduler():
    schedule.every().day.at("00:00").do(db.update_to_true_status)
    schedule.every(5).minutes.do(db.update_user_levels)
    schedule.every(13).minutes.do(db.update_global_part)
    schedule.every(12).hours.do(send_database_dump)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    dp.loop.create_task(daily_scheduler())
    executor.start_polling(dp, skip_updates=True)
