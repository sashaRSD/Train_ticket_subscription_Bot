from pyfiglet import Figlet
from dir_bot import create_bot, client
import aioschedule, asyncio


async def scheduler():
    aioschedule.every().day.at('21:02').do(client.timer_fun)
    aioschedule.every().day.at('12:00').do(client.timer_fun)
    aioschedule.every().day.at('16:00').do(client.timer_fun)
    aioschedule.every().day.at('20:00').do(client.timer_fun)
    aioschedule.every().day.at('21:00').do(client.timer_fun)
    aioschedule.every().day.at('22:00').do(client.timer_fun)
    aioschedule.every().day.at('23:00').do(client.timer_fun)
    aioschedule.every().day.at('23:30').do(client.timer_fun)
    aioschedule.every().day.at('23:50').do(client.timer_fun)
    print('Timer run!')
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup():
    print('ok2')
    preview_text = Figlet(font='slant')
    print(preview_text.renderText("TICKET SUB BOT"))
    asyncio.create_task(scheduler())


async def main():
    create_bot.dp.startup.register(on_startup)
    await create_bot.dp.start_polling(create_bot.bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
