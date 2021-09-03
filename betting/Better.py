from betting.broker_ifortuna import IFortuna
from betting.Exceptions.BetRuntimeException import BetRuntimeException
from multiprocessing import Pool
from typing import List
from betting.better_config import ALLOWED_BETS_PER_SPORT, ALLOWED_SPORTS, BROKERS_ACCOUNTS
from asgiref.sync import async_to_sync


class Better:
    
    def __init__(self, dc_bet_cog) -> None:
        self.bet_cog = dc_bet_cog
        self.brokers = self._init_brokers(BROKERS_ACCOUNTS)
        self.status_messages = []

    def _init_brokers(self, brokers_accounts: dict) -> dict:
        inited_brokers = {}
        for broker, account in brokers_accounts.items():
            inited_brokers[broker] = (self._init_broker(broker), account)
        return inited_brokers

    def _init_broker(self, broker: str):
        if broker == 'IFortuna':
            return IFortuna()
        else:
            print('Init Better Error: broker not found.')

    def bet_all_accounts(self, command: str) -> List[dict]:
        bet_info = {}
        try:
            bet_info = self._process_bet_command(command)
        except Exception as e:
            # this will send error to discord
            self.bet_cog.bot.stdout.send(e)

        pool = Pool(processes=len(self.brokers.keys()))
        brokers_event_results = {}
        for broker, _ in self.brokers.values():
            brokers_event_results[str(broker)] = pool.apply_async(broker.find_event, (bet_info['event'],)).get()
        brokers_to_bet = async_to_sync(self.bet_cog.send_for_approval)(brokers_event_results, bet_info)
        
        for broker, account in self.brokers.values():
            if brokers_to_bet[str(broker)]:
                pool.apply_async(
                    broker.bet, 
                    args=(account, bet_info), 
                    callback=self.status_messages_update
                )
                
        pool.close()
        pool.join()
        bet_reports = self.status_messages
        self.clear_status_messages()
        return bet_reports

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
        return {'event': event, 'bet': bet, 'specs': specs, 'sport': sport}

    
