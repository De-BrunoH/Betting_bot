import asyncio
from asgiref.sync import sync_to_async
from my_discord.bot.dc_bot import Bet_dc_bot
from discord.ext.commands import Cog, command, Context
from concurrent.futures import ThreadPoolExecutor

class Bet(Cog):
    def __init__(self, bot: Bet_dc_bot):
        self.bot = bot

    @command()
    async def hello(self, ctx):
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @command(name='bet', aliases=('b',))
    async def place_bets_all_accounts(self, context: Context):
        await sync_to_async(self.bot.better.bet_all_accounts)(context.fetch_message)
        # TODO:
        #   + bet_all_accounts should append messages to better.status_messages
        #   + in this method should all messages eb send to channel for discord user to inspect 
        self.bot.better.clear_status_messages()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('bet')

    
def setup(bot: Bet_dc_bot):
    bot.add_cog(Bet(bot))