'''from telethon import TelegramClient, events
import os
from keep_alive import keep_alive

api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
alex = 'alex'
bruno = 'bruno'

client_a = TelegramClient(alex, api_id, api_hash)
source_channel_a = -1001257344761
dump_channel_a = -1001322443667

client_b = TelegramClient(bruno, api_id, api_hash)
source_user_b = 'Huzvo'
source_channel_b = -1001322443667
dump_channel_b = -568281812

@client_a.on(events.NewMessage(chats=source_channel_a))
async def listener_a(event):
    await client_a.send_message(entity=dump_channel_a, message=event.message)


@client_b.on(events.NewMessage(chats=source_channel_b))#, from_users=source_user_b))
async def listener_b(event):
    await client_b.send_message(entity=dump_channel_b, message=event.message)

with client_b:
    with client_a:
      keep_alive()
      client_a.run_until_disconnected()
      client_b.run_until_disconnected()'''