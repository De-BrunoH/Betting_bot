from my_discord.bot.dc_bot import Bet_dc_bot
from logging.config import fileConfig

''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (3)') '''


if __name__ == '__main__':

    bot = Bet_dc_bot()
    bot.run()


'''
$bet
futbal 
Petržalka
Zápas: presný počet gólov
2
'''