from telethon import TelegramClient
import asyncio

# Replace these with your values from my.telegram.org
api_id = 20958489
api_hash = '26cced738312af659e97343ad1eab8e7'
phone_number = '+77021110775'  # Your phone number with country code, e.g. +123456789

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Connect and sign in if necessary
    # Use 'phone=' instead of 'phone_number='
    await client.start(phone=phone_number)

    # The group username or ID
    entity = await client.get_entity('https://t.me/+x6oDe91UWw9lMTUy')  # if you have an invite link
    group = entity
    # group = '-1002374154188'  # If this is not a username or ID, you may need the numeric ID

    # Fetch messages
    all_messages = []
    async for message in client.iter_messages(group, limit=None):
        if message.text and message.sender_id:
          sender_id = message.sender_id
          msg_text = message.text.replace('\n', ' ')
          all_messages.append((sender_id, msg_text))


    # Save messages to a file
    with open('group_messages.txt', 'w', encoding='utf-8') as f:
        for sender_id, msg in all_messages:
            f.write(f"{sender_id}|{msg}\n")

with client:
    client.loop.run_until_complete(main())
