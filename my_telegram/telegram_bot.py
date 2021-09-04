from telethon import TelegramClient, events

api_id = '7662193'
api_hash = '492ffc256dff3e5c7b5f351d38f59515'
name = '+421915379988'

client = TelegramClient(name, api_id, api_hash)
source_channel = -444167156
dump_channel = -585788900 # channel id alexovej groupy pridaj bota posli tu spravu a hotovo zistis cez web telegram ez
source_user = 'me' # sem dam klacovho sefa username

@client.on(events.NewMessage(chats=source_channel, from_users=source_user))
async def listener(event):
    await client.forward_messages(entity=dump_channel, messages=event.message)
    client.get_entity()
with client:
    client.run_until_disconnected()