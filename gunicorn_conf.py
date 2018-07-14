import asyncio

from bot import bot, WEBHOOK_URL


def on_starting(server):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.delete_webhook())
    loop.run_until_complete(bot.set_webhook(WEBHOOK_URL))
