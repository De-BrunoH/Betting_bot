import asyncio
from typing import Tuple
from asgiref.sync import sync_to_async
from discord.colour import Color
from my_discord.bot.dc_bot import Bet_dc_bot
from discord.ext.commands import Cog, command, Context
from discord import Embed, Colour, File

class Bet(Cog):
    def __init__(self, bot: Bet_dc_bot):
        self.bot = bot

    @command()
    async def hello(self, ctx):
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @command(name='bet', aliases=('b',))
    async def place_bets_all_accounts(self, ctx: Context, *, arg):
        reports = await sync_to_async(self.bot.better.bet_all_accounts)(arg)
        for report in reports:
            formated_report, files = await self.format_report(report)
            await self.bot.stdout.send(files=files, embed=formated_report)

    async def format_report(self, report: dict) -> Embed:
        broker_color, broker_logo_path = await self.get_broker_visuals(report['broker'])
        formated_report = Embed(
            title = '{} bet report:'.format(report['broker']),
            color = broker_color
        )

        
        broker_logo = broker_logo_path.split('/')[-1]
        tnail = File(broker_logo_path, filename=broker_logo)
        formated_report.set_thumbnail(url='attachment://' + broker_logo)

        formated_report.add_field(name='Sport:', value=report['sport'])
        formated_report.add_field(name='Event:', value=report['event'])
        formated_report.add_field(name='Specs:', value=report['bet'] + '\n' + report['specs'])
        formated_report.add_field(name='Allocation:', value=report['allocation'])
        formated_report.add_field(name='Bet rate:', value=report['bet_rate'])
        formated_report.add_field(name='Possible win:', value=report['possible_win'])

        bet_confirmation_path = report['confirmation_img']
        bet_confirmation = bet_confirmation_path.split('/')[-1]
        confirmation = File(bet_confirmation_path, filename=bet_confirmation)
        formated_report.set_image(url='attachment://' + bet_confirmation)

        formated_report.set_footer()
        return formated_report, [tnail, confirmation]

    async def get_broker_visuals(self, broker: str) -> Tuple[Colour, str]:
        if broker == 'IFortuna':
            return Colour.from_rgb(255, 219, 1), './betting/broker_logos/ifortunalogo.png'

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('bet')

    
def setup(bot: Bet_dc_bot):
    bot.add_cog(Bet(bot))