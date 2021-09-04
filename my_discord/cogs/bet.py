import asyncio
from betting.Better import Better
from typing import List, Tuple
from asgiref.sync import sync_to_async
from my_discord.bot.dc_bot import Bet_dc_bot
from discord.ext.commands import Cog, command, Context
from discord import Embed, Colour, File

class Bet(Cog):
    def __init__(self, bot: Bet_dc_bot):
        self.bot = bot
        self.better = Better(self)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('bet')

    @command()
    async def hello(self, ctx):
        await ctx.channel.send(f'Hello {ctx.author.mention}!')

    @command(name='bet', aliases=('b',))
    async def place_bets_all_accounts(self, ctx: Context, *, arg):
        reports = await sync_to_async(self.better.bet_all_accounts)(arg)
        for report in reports:
            await self.send_report(report)
            
    async def send_report(self, report: dict) -> None:
        formated_report, files = await self.format_bet_report(report)
        await self.bot.stdout.send(files=files, embed=formated_report)

    async def format_bet_report(self, report: dict) -> Tuple[Embed, List[File]]:
        if 'exception' in report.keys():
            return await self.format_bet_exception_report(report)
        return await self.format_bet_result_report(report)
    
    async def format_bet_result_report(self, report: dict) -> Tuple[Embed, List[File]]:
        formated_report, tnail = await self.create_bet_embed_base(report['broker'], '{} bet result report:'.format(report['broker']))

        formated_report.add_field(name='Sport:', value=report['sport'], inline=True)
        formated_report.add_field(name='Event:', value=report['event'], inline=True)
        formated_report.add_field(name='Specs:', value=report['bet'] + '\n' + report['specs'], inline=True)
        formated_report.add_field(name='Allocation:', value=report['allocation'], inline=True)
        formated_report.add_field(name='Bet rate:', value=report['bet_rate'], inline=True)
        formated_report.add_field(name='Possible win:', value=report['possible_win'], inline=True)

        bet_confirmation_path = report['confirmation_img']
        bet_confirmation = bet_confirmation_path.split('/')[-1]
        confirmation_img = File(bet_confirmation_path, filename=bet_confirmation)
        formated_report.set_image(url='attachment://' + bet_confirmation)

        formated_report.set_footer(text='Bet successful!')
        return formated_report, [tnail, confirmation_img]

    async def format_bet_exception_report(self, report: dict) -> Tuple[Embed, List[File]]:
        formated_report, tnail = await self.create_bet_embed_base(report['broker'], '{} bet exception report:'.format(report['broker']))

        formated_report.add_field(name='Event:', value=report['exception'].event, inline=True)
        formated_report.add_field(name='Exception message:', value=report['exception'].message, inline=True)
        formated_report.add_field(name='Root exception message:', value=report['exception'].root_message, inline=True)
        
        bet_exception_path = report['exception'].screenshot
        bet_exception = bet_exception_path.split('/')[-1]
        exception_img = File(bet_exception_path, filename=bet_exception)
        formated_report.set_image(url='attachment://' + bet_exception)

        formated_report.set_footer(text='Bet skipped.')
        return formated_report, [tnail, exception_img]

    async def create_bet_embed_base(self, broker: str, title: str) -> Tuple[Embed, File]:
        broker_color, broker_logo_path = await self.get_broker_visuals(broker)
        embed = Embed(
            title = title,
            color = broker_color
        )
        broker_logo = broker_logo_path.split('/')[-1]
        tnail = File(broker_logo_path, filename=broker_logo)
        embed.set_thumbnail(url='attachment://' + broker_logo)
        return embed, tnail

    async def get_broker_visuals(self, broker: str) -> Tuple[Colour, str]:
        if broker == 'IFortuna':
            return Colour.from_rgb(255, 219, 1), './betting/broker_logos/ifortunalogo.png'

    async def send_for_approval(self, brokers_event: dict, bet_info: dict) -> dict:
        approval_flags = {}
        for broker, event_findings in brokers_event.items():
            if 'exception' not in event_findings.keys():
                approval_flags[broker] = await self.get_approval(broker, event_findings['event_img'], bet_info)
            else:
                approval_flags[broker] = False
                await self.send_report(event_findings)
        return approval_flags

    async def get_approval(self, broker: str, event_img: str, bet_info: dict) -> bool:
        user_decision_embed, files = await self.create_user_decision_embed(
            broker, 
            event_img, 
            bet_info
        )
        message = await self.bot.stdout.send(files=files, embed=user_decision_embed)
        thumb_up = '👍'
        thumb_down = '👎'
        await message.add_reaction(thumb_up)
        await message.add_reaction(thumb_down)
        def check(reaction, user):
            return user in self.bot.legit_users and str(
                reaction.emoji) in [thumb_up, thumb_down]
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=600)
        except asyncio.TimeoutError:
            self.bot.stdout.send(f'Broker {broker}: You haven\'t made a decision, the bet is closed.')
            return False
        if str(reaction.emoji) == thumb_up:
            await self.bot.stdout.send(f'Broker {broker}: Betting...')
            return True
        if str(reaction.emoji) == thumb_down:
            await self.bot.stdout.send(f'Broker {broker}: The bet is closed.')
            return False
        return False

    async def create_user_decision_embed(self, broker: str, event_img_path: str, bet_info: dict) -> Tuple[Embed, List[File]]:
        embed, tnail = await self.create_bet_embed_base(broker, f'{broker} broker bet confirmation:')

        embed.add_field(name='Sport:', value=bet_info['sport'], inline=True)
        embed.add_field(name='Event:', value=bet_info['event'], inline=True)
        embed.add_field(name='Specs:', value=bet_info['bet'] + '\n' + bet_info['specs'], inline=True)

        event_screen = event_img_path.split('/')[-1]
        event_img = File(event_img_path, filename=event_screen)
        embed.set_image(url='attachment://' + event_screen)

        embed.set_footer(text='DECISION REQUIRED')
        return embed, [tnail, event_img]

    
def setup(bot: Bet_dc_bot):
    bot.add_cog(Bet(bot))