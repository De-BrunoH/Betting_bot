from my_discord.bot.dc_bot import Bet_dc_bot

''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (3)') '''
TEST_COMMAND = 'futbal\nSportivo Belgrano\nZápas: počet gólov\nMenej ako (2.5)'

if __name__ == '__main__':
    bot = Bet_dc_bot()
    bot.run()


'''
$bet
futbal 
Zvezda St.Petersburg|FC Chita
Zápas: počet gólov
Menej ako (3)
'''