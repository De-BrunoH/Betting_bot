from betting.better_config import ACCOUNTS_IFORTUNA, TEST_COMMAND
from betting.broker_ifortuna import IFortuna
from betting.Better import Better
from my_discord.bot.dc_bot import Bet_dc_bot

''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (3)') '''
TEST_COMMAND = 'futbal\nPerth SC\nZápas: počet gólov\nMenej ako (3.5)'

if __name__ == '__main__':
    #bot = Bet_dc_bot()
    #bot.run()
    IFortuna().bet(ACCOUNTS_IFORTUNA[0], Better()._process_bet_command(TEST_COMMAND))