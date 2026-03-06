import os
import pymongo

from telebot.async_telebot import AsyncTeleBot

from base_func import Shortener

bot = AsyncTeleBot(os.environ['TELEGRAM_TOKEN'], parse_mode=None)
mongo_client = pymongo.AsyncMongoClient("mongodb://admin:password@localhost:27017")
db = mongo_client['shorter_urls_db']
urls_collection = db['urls']
BASE_URL = "http://127.0.0.1:8000"


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['stat'])
async def send_statistic(message):
    user_id = message.from_user.id
    user_urls = await urls_collection.find({"user_id": user_id}).to_list()
    user_text = f"Your URLs:\n" + "\n".join([f"{itm.get('long_url')} -> {itm.get('clicks')}\n" for itm in user_urls])
    await bot.reply_to(message, user_text)


@bot.message_handler(func=lambda message: True)
async def process_text_message(message):
    short_url = await Shortener.create_short_url(urls_collection, message.text, message.from_user.id)
    await bot.reply_to(message.chat.id, f"short url: {BASE_URL}/{short_url}")


if __name__ == '__main__':
    import asyncio

    asyncio.run(bot.polling())
