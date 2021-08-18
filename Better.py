from better_config import ACCOUNTS_IFORTUNA, ALLOWED_BETS_PER_SPORT, ALLOWED_SPORTS
from broker_ifortuna import IFortuna
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

class Better:
    driver = None
    brokers = {
        'IFortuna': (IFortuna(), ACCOUNTS_IFORTUNA)
    }
    
    def __init__(self, browser_driver: WebDriver) -> None:
        self.driver = browser_driver

    def process_bet(self, command: str) -> None:
        bet_info = {}
        try:
            bet_info = self._process_bet_command(command)
        except Exception as e:
            # this will send error to discord
            print(e)
        for broker, accounts in self.brokers.values():
            broker.setup_broker(self.driver)
            for account in accounts:
                broker.bet(self.driver, account['name'], account['password'], bet_info)

    def _process_bet_command(self, command: str) -> dict:
        ''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (2.5)') '''
        parsed_command = command.strip().split('\n')
        parsed_command = [part.strip() for part in parsed_command if len(part.strip()) != 0]
        if len(parsed_command) != 4:
            raise Exception('Error: command has too many parts.')
        sport, event, bet, specs = parsed_command
        if sport not in ALLOWED_SPORTS:
            raise Exception('Error: Sport not supported.')
        if bet not in ALLOWED_BETS_PER_SPORT[sport]:
            raise Exception('Error: Bet not supported.')
        return {'event': event, 'bet': bet, 'specs': specs}

        


    
            





