from telethon import TelegramClient, events
import os
from keep_alive import keep_alive

api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
name = os.environ['PHONE_NUMBER']

client = TelegramClient(name, api_id, api_hash)
source_channel = -444167156
dump_channel = -585788900 # channel id alexovej groupy pridaj bota posli tu spravu a hotovo zistis cez web telegram ez
source_user = 'me' # sem dam klacovho sefa username

@client.on(events.NewMessage(chats=source_channel, from_users=source_user))
async def listener(event):
    await client.send_message(entity=dump_channel, message=event.message)

with client:
    keep_alive()
    client.run_until_disconnected()