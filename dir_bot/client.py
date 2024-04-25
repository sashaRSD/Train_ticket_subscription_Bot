from aiogram import types
from aiogram.filters import Command
from dir_bot import create_bot
from dir_get import get
import asyncio

id_admin = create_bot.id_admin
id_admin2 = create_bot.id_admin2
dp = create_bot.dp
bot = create_bot.bot

@dp.message(Command('start'))
async def commands_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, f'Добрый день, {message.from_user.first_name}! 👋\n'
                                                     f'Теперь ты будещь шарить про билеты! 😉\n\n'
                                                     f'Если нужна инфа, то вот → /get')
    except:
        await message.delete()
        await bot.send_message(message.from_user.id, 'Напишите мне в личные сообщения')


@dp.message(Command('get'))
async def get_fun(message: types.Message):
    data = await get.scraping_yandex()
    for i_data in data:
        await bot.send_message(message.from_user.id, i_data[1], parse_mode="html")


async def timer_fun():
    data = await get.scraping_yandex()
    for i_data in data:
        if i_data[0]:
            await bot.send_message(id_admin, i_data[1], parse_mode="html")
            await bot.send_message(id_admin2, i_data[1], parse_mode="html")


@dp.message()
async def other(message: types.Message):
    await message.delete()
    smile = await bot.send_message(message.from_user.id, '🗿')
    await asyncio.sleep(4)
    await bot.delete_message(chat_id=message.from_user.id, message_id=smile.message_id)
