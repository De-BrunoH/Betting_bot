from betting.brokers.doxxbet.doxxbet import Doxxbet
import logging
from betting.brokers.ifortuna.ifortuna import IFortuna
from multiprocessing import Pool
from typing import List
from betting.better.better_config import ALLOWED_BETS_PER_SPORT, ALLOWED_SPORTS, BROKERS_ACCOUNTS
from asgiref.sync import async_to_sync
from logger.bet_logger import setup_logger

logger = setup_logger('better')

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
        elif broker == 'Doxxbet':
            return Doxxbet()
        else:
            print('Init Better Error: broker not found.')

    def bet_all_accounts(self, command: str) -> List[dict]:
        logger.info('Bet all accounts start.')
        bet_info = self._handle_bet_command(command)
        if not bet_info:
            return []
        pool = Pool(processes=len(self.brokers.keys()))
        self._process_relevant_brokers(pool, self._get_relevant_brokers(pool, bet_info), bet_info)
        pool.close()
        pool.join()
        bet_reports = self.status_messages
        self._clear_status_messages()
        return bet_reports

    def _process_relevant_brokers(self, pool, brokers_to_bet: dict, bet_info: dict) -> None:
        to_process = [broker + ' : ' + str(0 < processed) for broker, processed in brokers_to_bet.items()]
        logger.info(f'Processing relevant brokers: {to_process}.')
        for broker, account in self.brokers.values():
            if brokers_to_bet[str(broker)] != -1:
                pool.apply_async(
                    broker.bet, 
                    args=(account, bet_info, brokers_to_bet[str(broker)]), 
                    callback=self._status_messages_update
                )

    def _get_relevant_brokers(self, pool, bet_info: dict) -> dict:
        event_name = bet_info['event']
        logging.info(f'Finding relevant brokers for event {event_name}.')
        brokers_event_results = {}
        for broker, _ in self.brokers.values():
            brokers_event_results[str(broker)] = pool.apply_async(
                broker.find_event,
                args=(bet_info['event'],)
            )
        for broker, _ in self.brokers.values():
            brokers_event_results[str(broker)] = brokers_event_results[str(broker)].get()
        return async_to_sync(self.bet_cog.send_for_approval)(brokers_event_results, bet_info)

    def _handle_bet_command(self, command: str) -> dict:
        logger.info('Handling command: ' + f'{command}')
        bet_info = {}
        try:
            bet_info = self._process_bet_command(command)
        except Exception as e:
            logger.info('Received command is has incorrect format.')
            self.bet_cog.bot.stdout.send(e)
        return bet_info
    
    def _status_messages_update(self, message_data: dict) -> None:
        self.status_messages.append(message_data)
    
    def _clear_status_messages(self) -> None:
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
            raise Exception('Error: Bet type not supported for this sport.')
        return {'event': event, 'bet': bet, 'specs': specs, 'sport': sport}

    
