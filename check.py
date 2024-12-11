from telethon import TelegramClient

api_id = 20958489
api_hash = '26cced738312af659e97343ad1eab8e7'
phone_number = '+77021110775'  # Your phone number with country code, e.g. +123456789

client = TelegramClient('session_name', api_id, api_hash)

async def print_dialogs():
    await client.start(phone=phone_number)
    dialogs = await client.get_dialogs()
    for d in dialogs:
        print(d.name, d.id, d.entity)

with client:
    client.loop.run_until_complete(print_dialogs())
