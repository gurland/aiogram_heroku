import os
from urllib.parse import urljoin
from random import choice

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.utils import context
from aiogram.dispatcher.webhook import get_new_configured_app
from lxml import etree

TOKEN = os.getenv('TOKEN', '')  # Press "Reveal Config Vars" in settings tab on Heroku and set TOKEN variable
PROJECT_NAME = os.getenv('PROJECT_NAME', 'aiogram-example')  # Set it as you've set TOKEN env var

WEBHOOK_HOST = f'https://{PROJECT_NAME}.herokuapp.com/'  # Enter here your link from Heroku project settings
WEBHOOK_URL_PATH = '/webhook/' + TOKEN
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

# Inline keyboard initialization with one refresh button
inline_keyboard = types.InlineKeyboardMarkup()
random_button = types.InlineKeyboardButton('Получить случайную цитату', callback_data='refresh')
inline_keyboard.add(random_button)

bot = Bot(TOKEN)
dp = Dispatcher(bot)


async def get_random_bash_quote():
    """Downloads bash.im/random page, parses it and returns random quote"""
    bash_url = 'https://bash.im/random'

    async with aiohttp.ClientSession() as session:
        async with session.get(bash_url) as resp:
            html = await resp.text()

    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)
    quote_tags = tree.xpath('//div[@class="text"]')  # Xpath is a query language for selecting specific tags
    random_quote_tag = choice(quote_tags)
    random_quote = '\n'.join(random_quote_tag.itertext())  # The easiest way to get text inside tag divided by br tags
    return random_quote


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """Handle start command"""
    random_quote = await get_random_bash_quote()
    await message.reply(random_quote, reply_markup=inline_keyboard)


@dp.callback_query_handler(func=lambda cb: True)
async def process_callback_data(callback_query: types.CallbackQuery):
    """Handle all callback data which is being sent to bot"""
    action = callback_query.data

    if action == 'refresh':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        random_quote = await get_random_bash_quote()
        await bot.edit_message_text(random_quote, chat_id, message_id, reply_markup=inline_keyboard)


async def on_startup(app):
    """Simple hook for aiohttp application which manages webhook"""
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)


if __name__ == '__main__':
    # Create aiohttp.web.Application with configured route for webhook path
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    app.on_startup.append(on_startup)
    dp.loop.set_task_factory(context.task_factory)
    web.run_app(app, host='0.0.0.0', port=os.getenv('PORT'))  # Heroku stores port you have to listen in your app
