import logging
import os
import random
from collections import defaultdict, Counter
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
from datetime import datetime, time, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

TOKEN = '7648682155:AAH47YWYgpSCIsxjpoA7aHB1Ic5Y0UDbmK8'

CHAT_ID = -1002374154188  # Replace with your target group chat ID

user_messages = defaultdict(list)
love_quotes = []
love_photos_dir = 'love_photos'

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

async def mylove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_quote = random.choice(love_quotes) if love_quotes else "Я люблю тебя больше, чем могу выразить словами."
    photo_path = None
    if os.path.isdir(love_photos_dir):
        photos = [f for f in os.listdir(love_photos_dir) if os.path.isfile(os.path.join(love_photos_dir, f))]
        if photos:
            chosen_photo = random.choice(photos)
            photo_path = os.path.join(love_photos_dir, chosen_photo)

    if photo_path and os.path.isfile(photo_path):
        await update.message.reply_photo(photo=open(photo_path, 'rb'), caption=chosen_quote)
    else:
        await update.message.reply_text(chosen_quote)

async def kezdesu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_kezdesu_message(context.bot, update.effective_chat.id)

async def send_kezdesu_message(bot, chat_id):
    now = datetime.now()
    current_year = now.year
    target_date = datetime(current_year, 12, 28)

    if target_date < now:
        target_date = datetime(current_year + 1, 12, 28)

    delta = target_date - now
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    reply = f"Осталось {days} дней, {hours} часов и {minutes} минут до встречи с моей родственной душой (28 декабря)."
    await bot.send_message(chat_id=chat_id, text=reply)

# This job runs automatically at midnight everyday
async def kezdesu_job(context: ContextTypes.DEFAULT_TYPE):
    await send_kezdesu_message(context.bot, CHAT_ID)  # Send to known chat ID

def main():
    load_previous_messages()
    load_quotes()

    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CommandHandler('topmessages', top_messages))
    app.add_handler(CommandHandler('listusers', list_users))
    app.add_handler(CommandHandler('leaderboard', leaderboard))
    app.add_handler(CommandHandler('mylove', mylove))
    app.add_handler(CommandHandler('kezdesu', kezdesu))

    # Schedule a job to run daily at 00:00 (midnight)
    # You must ensure that the server time is correct.
    # If you want to handle timezones, adjust accordingly.
    job_queue = app.job_queue
    job_queue.run_daily(kezdesu_job, time=time(0,0,0))  # midnight

    app.run_polling()

if __name__ == '__main__':
    main()
