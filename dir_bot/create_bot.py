from aiogram import Bot
from aiogram import Dispatcher
import configparser
config = configparser.ConfigParser()
config.read("dir_bot/config.ini")

id_admin = config["TOKEN"]["id_admin"]

bot = Bot(token=config["TOKEN"]["token_bot_test"])
dp = Dispatcher()
