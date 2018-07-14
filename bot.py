import os
from urllib.parse import urljoin
from random import choice

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.webhook import get_new_configured_app
from lxml import etree

TOKEN = os.getenv('TOKEN', '')  # Press "Reveal Config Vars" in settings tab on heroku and set TOKEN variable

WEBHOOK_HOST = 'https://aiogram-example.herokuapp.com/'  # Enter here your link from heroku project settings
WEBHOOK_URL_PATH = '/webhook/' + TOKEN
WEBHOOK_URL = urljoin(WEBHOOK_HOST, WEBHOOK_URL_PATH)

# Inline keyboard initialization with one refresh button
inline_keyboard = types.InlineKeyboardMarkup()
random_button = types.InlineKeyboardButton('Получить случайную запись', callback_data='refresh')
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
    random_quote = await get_random_bash_quote()
    await message.reply(random_quote, reply_markup=inline_keyboard)


@dp.callback_query_handler(func=lambda cb: True)
async def process_callback_data(callback_query: types.CallbackQuery):
    action = callback_query.data

    if action == 'refresh':
        message_id = callback_query.message.message_id
        chat_id = callback_query.message.chat.id
        random_quote = await get_random_bash_quote()
        await bot.edit_message_text(random_quote, chat_id, message_id, reply_markup=inline_keyboard)


async def get_web_app():
    app = get_new_configured_app(dp, WEBHOOK_URL_PATH)
    app.add_routes([web.get('/', test)])
    return app


async def test(request):
    return web.Response(text="Hello, world")
