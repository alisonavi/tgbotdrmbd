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
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '7648682155:AAH47YWYgpSCIsxjpoA7aHB1Ic5Y0UDbmK8'


# Dictionary to store messages per user
user_messages = defaultdict(list)

# Global lists for quotes and photos
love_quotes = []
love_photos_dir = 'love_photos'  # Directory containing photos

def load_previous_messages():
    # Load historical messages from group_messages.txt if it exists
    if os.path.exists('group_messages.txt'):
        with open('group_messages.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    user_id_str, msg = line.split('|', 1)
                    user_id = int(user_id_str)
                    user_messages[user_id].append(msg)

def load_quotes():
    # Load quotes from love_quotes.txt
    if os.path.exists('love_quotes.txt'):
        with open('love_quotes.txt', 'r', encoding='utf-8') as f:
            for line in f:
                quote = line.strip()
                if quote:
                    love_quotes.append(quote)
    else:
        # If file not found, just add a fallback quote
        love_quotes.append("Я люблю тебя больше, чем могу выразить словами.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_messages[user_id].append(message)
    logging.info(f"Recorded message from user_id {user_id}, username @{username}: {message}")

async def get_most_frequent_messages(user_id):
    messages = user_messages[user_id]
    counter = Counter(messages)
    most_common = counter.most_common(5)  # Top 5 messages
    return most_common

async def top_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        identifier = context.args[0].lstrip('@')
        user_id = None

        # Try to interpret the identifier as an integer user ID
        try:
            identifier_int = int(identifier)
            if identifier_int in user_messages:
                user_id = identifier_int
        except ValueError:
            # If not an integer, proceed to check username
            pass

        # If user_id is still None, try to match username or first name
        if user_id is None:
            for uid in user_messages:
                user = await context.bot.get_chat(uid)
                # Check by username or first name
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
        # Show top messages for the command sender
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

    # Create a list of tuples: (user_id, message_count)
    counts = [(uid, len(msgs)) for uid, msgs in user_messages.items()]

    # Sort by message count descending
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
    # Choose a random quote from loaded quotes
    if not love_quotes:
        chosen_quote = "Я люблю тебя больше, чем могу выразить словами."  # fallback
    else:
        chosen_quote = random.choice(love_quotes)

    # Get a random photo from the love_photos directory
    if os.path.isdir(love_photos_dir):
        photos = [f for f in os.listdir(love_photos_dir) if os.path.isfile(os.path.join(love_photos_dir, f))]
        if photos:
            chosen_photo = random.choice(photos)
            photo_path = os.path.join(love_photos_dir, chosen_photo)
        else:
            photo_path = None
    else:
        photo_path = None

    if photo_path and os.path.isfile(photo_path):
        await update.message.reply_photo(photo=open(photo_path, 'rb'), caption=chosen_quote)
    else:
        # If no photo found, just send the quote as text
        await update.message.reply_text(chosen_quote)

# New command: /kezdesu
# This command shows time remaining until December 28 of the current year.
async def kezdesu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    current_year = now.year

    # Target date: December 28 of the current year
    target_date = datetime(current_year, 12, 29)

    # If the date has passed for this year, set the target to next year
    if target_date < now:
        target_date = datetime(current_year + 1, 12, 28)

    delta = target_date - now

    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    reply = f"Жаныммен кездескенше {days} күн, {hours-5} сағат {minutes} минут қалды."
    await update.message.reply_text(reply)

def main():
    # Load old messages from file
    load_previous_messages()

    # Load quotes from external file
    load_quotes()

    app = ApplicationBuilder().token(TOKEN).build()

    # Handler to collect all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Command handlers
    app.add_handler(CommandHandler('topmessages', top_messages))
    app.add_handler(CommandHandler('listusers', list_users))
    app.add_handler(CommandHandler('leaderboard', leaderboard))
    app.add_handler(CommandHandler('mylove', mylove))
    app.add_handler(CommandHandler('kezdesu', kezdesu))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
