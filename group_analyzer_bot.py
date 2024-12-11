import logging
import os
import random
from collections import defaultdict, Counter
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
TOKEN = '7648682155:AAH47YWYgpSCIsxjpoA7aHB1Ic5Y0UDbmK8'


user_messages = defaultdict(list)
love_quotes = []
love_photos_dir = 'love_photos'

# Queues for quotes and photos
quotes_queue = []
photos_queue = []

def load_previous_messages():
    if os.path.exists('group_messages.txt'):
        with open('group_messages.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    user_id_str, msg = line.split('|', 1)
                    user_id = int(user_id_str)
                    user_messages[user_id].append(msg)

def load_quotes():
    if os.path.exists('love_quotes.txt'):
        with open('love_quotes.txt', 'r', encoding='utf-8') as f:
            for line in f:
                quote = line.strip()
                if quote:
                    love_quotes.append(quote)
    else:
        love_quotes.append("Я люблю тебя больше, чем могу выразить словами.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message.startswith('/'):
        # It's a command, do not record it
        return
    user_id = update.message.from_user.id
    user_messages[user_id].append(message)
    logging.info(f"Recorded message from user_id {user_id}")

async def get_most_frequent_messages(user_id):
    messages = user_messages[user_id]
    counter = Counter(messages)
    return counter.most_common(5)

async def top_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        identifier = context.args[0].lstrip('@')
        user_id = None

        try:
            identifier_int = int(identifier)
            if identifier_int in user_messages:
                user_id = identifier_int
        except ValueError:
            pass

        if user_id is None:
            for uid in user_messages:
                user = await context.bot.get_chat(uid)
                if user.username == identifier or user.first_name == identifier:
                    user_id = uid
                    break

        if user_id is None:
            await update.message.reply_text("Пайдаланушы табылмады немесе хабарламалар тіркелмеген.")
            return

        most_common = await get_most_frequent_messages(user_id)
        user = await context.bot.get_chat(user_id)
        reply = f"{user.first_name} үшін ең жиі жіберілген хабарламалар"
        if user.username:
            reply += f" (@{user.username})"
        reply += ":\n"
        for msg, count in most_common:
            reply += f'"{msg}": {count} рет\n'
        await update.message.reply_text(reply)
    else:
        user_id = update.message.from_user.id
        if user_id not in user_messages:
            await update.message.reply_text("Сіз үшін хабарламалар тіркелмеген.")
            return

        most_common = await get_most_frequent_messages(user_id)
        user = update.message.from_user
        reply = f"Сіздің ең жиі жіберілген хабарламаларыңыз, {user.first_name}:\n"
        for msg, count in most_common:
            reply += f'"{msg}": {count} рет\n'
        await update.message.reply_text(reply)

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user_messages:
        reply = "Хабарламалары тіркелген пайдаланушылар:\n"
        for uid in user_messages:
            user = await context.bot.get_chat(uid)
            if user.username:
                reply += f"- {user.first_name} (@{user.username})\n"
            else:
                reply += f"- {user.first_name} (ID: {uid})\n"
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Ешқандай пайдаланушы хабарлама жібермеген.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_messages:
        await update.message.reply_text("Ешқандай пайдаланушы хабарлама жібермеген.")
        return
    counts = [(uid, len(msgs)) for uid, msgs in user_messages.items()]
    counts.sort(key=lambda x: x[1], reverse=True)
    reply = "Хабарламалар саны бойынша көшбасшылар:\n"
    for uid, count in counts:
        user = await context.bot.get_chat(uid)
        if user.username:
            reply += f"{user.first_name} (@{user.username}): {count} хабарлама\n"
        else:
            reply += f"{user.first_name} (ID: {uid}): {count} хабарлама\n"
    await update.message.reply_text(reply)

def prepare_queues():
    global quotes_queue, photos_queue
    # Prepare quotes queue if needed
    if love_quotes:
        quotes_queue = random.sample(love_quotes, len(love_quotes))
    else:
        quotes_queue = ["Я люблю тебя больше, чем могу выразить словами."]

    # Prepare photos queue if available
    if os.path.isdir(love_photos_dir):
        photos = [f for f in os.listdir(love_photos_dir) if os.path.isfile(os.path.join(love_photos_dir, f))]
        if photos:
            photos_queue = random.sample(photos, len(photos))
        else:
            photos_queue = []
    else:
        photos_queue = []

async def mylove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global quotes_queue, photos_queue

    # If queues are empty or not initialized, prepare them
    if not quotes_queue:
        prepare_queues()

    chosen_quote = quotes_queue.pop(0)  # Take first item from quotes_queue
    photo_path = None

    if photos_queue:  # If we have photos
        chosen_photo = photos_queue.pop(0)  # Take first item from photos_queue
        photo_path = os.path.join(love_photos_dir, chosen_photo) if chosen_photo else None
        # If photos_queue is empty after popping, next time it'll regenerate

    if photo_path and os.path.isfile(photo_path):
        await update.message.reply_photo(photo=open(photo_path, 'rb'), caption=chosen_quote)
    else:
        # If no photo found or no photos at all, just send the quote
        await update.message.reply_text(chosen_quote)

# kezdesu command as before
async def kezdesu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_tz = ZoneInfo("Asia/Oral")
    now = datetime.now(tz=user_tz)
    current_year = now.year
    target_date = datetime(current_year, 12, 29, tzinfo=user_tz)
    if target_date < now:
        target_date = datetime(current_year + 1, 12, 28)
    delta = target_date - now
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    reply = f"Жаныммен кездескенше {days} күн, {hours} сағат {minutes+1} минут қалды."
    await update.message.reply_text(reply)

def fetch_random_joke():
    url = "https://www.anekdot.ru/random/story/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    joke_div = soup.find('div', class_='text')
    if joke_div:
        joke_text = joke_div.get_text(strip=True)
        joke_text = joke_text.replace('\xa0', ' ')
        joke_text = re.sub(r'\s+', ' ', joke_text).strip()
        return joke_text
    else:
        return "Не удалось получить шутку."

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke_text = fetch_random_joke()
    await update.message.reply_text(joke_text)

def main():
    load_previous_messages()
    load_quotes()

    # Initialize queues
    prepare_queues()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler('topmessages', top_messages))
    app.add_handler(CommandHandler('listusers', list_users))
    app.add_handler(CommandHandler('leaderboard', leaderboard))
    app.add_handler(CommandHandler('mylove', mylove))
    app.add_handler(CommandHandler('kezdesu', kezdesu))
    app.add_handler(CommandHandler('joke', joke))

    app.run_polling()

if __name__ == '__main__':
    main()
