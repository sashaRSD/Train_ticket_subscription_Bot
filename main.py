from aiogram.methods import DeleteWebhook
from pyfiglet import Figlet
from dir_bot import create_bot, client
from dir_base import base_train
from dir_get.get import params_city_in_travel
import aioschedule, asyncio


async def scheduler():
    aioschedule.every(len(params_city_in_travel)).minutes.do(client.timer_fun)
    aioschedule.every().day.at('00:00').do(base_train.sql_delete_old)
    print('Timer run!')
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup():
    asyncio.create_task(scheduler())
    base_train.sql_start()
    preview_text = Figlet(font='slant')
    print(preview_text.renderText("TICKET SUB BOT"))


async def main():
    create_bot.dp.startup.register(on_startup)
    await create_bot.bot(DeleteWebhook(drop_pending_updates=True))
    await create_bot.dp.start_polling(create_bot.bot)


if __name__ == '__main__':
    asyncio.run(main())
