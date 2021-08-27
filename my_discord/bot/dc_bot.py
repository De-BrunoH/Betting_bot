from asyncio import sleep
from betting.Better import Better
from my_discord.bot.dc_bot_config import TOKEN
from glob import glob
from selenium import webdriver
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot, CommandNotFound

DC_BOT_PREFIX = '$'
OWNER_ID = '291691766250471435'
SERVER_ID = 826572526573322270
SERVER_CHANNEL_ID = 879321122259234886
COGS = [path.split('/')[-1][:-3] for path in glob('./my_discord/cogs/*.py')]


class Ready(object):
    def __init__(self) -> None:
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'\t{cog} cog ready.')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bet_dc_bot(Bot):

    def __init__(self):
        self.PREFIX = DC_BOT_PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.stdout = None
        self.better = Better()

        print('Running bot...')
        super().__init__(command_prefix=DC_BOT_PREFIX, owner_ids=OWNER_ID,)

    def run(self):
        self.TOKEN = TOKEN
        print('Running setup...')
        self.setup()
        super().run(self.TOKEN, reconnect=True)

    def setup(self):
        for cog in COGS:
            self.load_extension(f'my_discord.cogs.{cog}')
            print(f'\t{cog} cog loaded.')
        print('Setup complete.')

    async def on_connect(self):
        print('Bot connected.')

    async def on_disconnect(self):
        print('Bot disconnected.')

    async def on_error(self, err: str, *args, **kwargs):
        if err == 'on_command_error':
            channel = args[0]
            await channel.send('Command error.')
        self.stdout.send('An error occured.')
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass
        elif hasattr(exc, 'original'):
            raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            
            self.guild = self.get_guild(SERVER_ID)
            self.stdout = self.get_channel(SERVER_CHANNEL_ID)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            await self.stdout.send('Betting bot online!')
            print('Ready to make some greens. (Bot ready)')
        else:
            print('Bot reconnected.')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)




