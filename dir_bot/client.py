from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.filters import Command
from dir_bot import create_bot
from dir_get import get

id_admin = create_bot.id_admin
dp = create_bot.dp
bot = create_bot.bot


@dp.message(Command('start'))
async def commands_start(message: types.Message):
    try:
        # text = get.scraping()
        await bot.send_message(message.from_user.id, f'Добрый день, {message.from_user.first_name}!\n'
                                                     f'Вы добавлены в ежедневную рассылку правильных слов!\n'
                                                     f'Чтобы отказаться - отправьте /stop')
    except:
        await message.delete()
        await bot.send_message(message.from_user.id,'Напишите мне в личные сообщения')


@dp.message(Command('Обратная_связь'))
async def commands_contact(message: types.Message):
    await message.answer('Наши контактные данные: \n'
                         'Электронная почта - kaa.1999@mail.ru \n'
                         'Username Telegram - @sasha_rsd')


@dp.message(Command('set', 'Получить_правильное_слово'))
async def commands_set(message: types.Message):
    text = get.scraping()
    await bot.send_message(message.from_user.id, text)


@dp.message(Command('Поддержать'))
async def commands_help(message: types.Message):
    text = 'Жми сюда!'
    url = 'https://www.tinkoff.ru/cf/71ARxuIBdob'
    url_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=text, url=url))
    await message.answer('Поддержать автора копейкой ;)', reply_markup=url_button)


@dp.message()
async def other(message: types.Message):
    await bot.send_message(message.from_user.id, 'Получить слово: /set\n'
                                                 'Отказаться от рассылки: /stop\n'
                                                 'Подписаться на расслыку: /start')


async def timer_fun():
    # data = get.scraping()
    await bot.send_message(id_admin, f'Добрый день!\n'
                                                 f'Вы добавлены в ежедневную рассылку правильных слов!\n'
                                                 f'Чтобы отказаться - отправьте /stop')
