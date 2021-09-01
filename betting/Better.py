from multiprocessing import Pool
from my_discord.bot.dc_bot import Bet_dc_bot
from betting.better_config import BROKERS, ALLOWED_BETS_PER_SPORT, ALLOWED_SPORTS


class Better:
    
    def __init__(self, bot: Bet_dc_bot) -> None:
        self.bot = bot
        self.brokers = BROKERS
        self.status_messages = []

    def bet_all_accounts(self, command: str) -> None:
        bet_info = {}
        try:
            bet_info = self._process_bet_command(command)
        except Exception as e:
            # this will send error to discord
            print(e)

        

        all_accounts = 0
        for broker, accounts in self.brokers.values():
            all_accounts += len(accounts)
        pool = Pool(processes=3)
        for broker, accounts in self.brokers.values():
            for account in accounts:
                pool.apply_async(broker.bet, args=(account, bet_info), callback=self.status_messages_update)
        pool.close()
        pool.join()

    def status_messages_update(self, message_data: dict) -> None:
        self.status_messages.append(message_data)
    
    def clear_status_messages(self) -> None:
        self.status_messages = []

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

    
