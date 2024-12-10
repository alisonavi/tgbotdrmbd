import logging
from collections import defaultdict, Counter
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '7648682155:AAH47YWYgpSCIsxjpoA7aHB1Ic5Y0UDbmK8'

# Dictionary to store messages per user
user_messages = defaultdict(list)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user_messages[user_id].append(message)
    logging.info(f"Recorded message from user_id {user_id}, username @{username}: {message}")

async def get_most_frequent_messages(user_id):
    messages = user_messages[user_id]
    counter = Counter(messages)
    most_common = counter.most_common(5)  # Adjust the number as needed
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

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler to collect all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Command handler to display top messages
    app.add_handler(CommandHandler('topmessages', top_messages))

    # Command handler to list users
    app.add_handler(CommandHandler('listusers', list_users))

    # Start the bot
    app.run_polling()
if __name__ == '__main__':
    main()
