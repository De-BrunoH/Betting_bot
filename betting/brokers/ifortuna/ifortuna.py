import logging
from betting.bet_exceptions.BetTimeoutException import BetTimeoutException
from selenium.webdriver.safari import webdriver
from betting.better.better_config import BET_WAIT_TIME, BOOKIE_DECISION_WAIT, BROKER_COMMANDS, MIN_BET_RATE
from betting.bet_exceptions.BetRuntimeException import BetRuntimeException
from betting.bet_exceptions.EventNotFoundException import EventNotFoundException
from typing import Optional, Tuple
from time import sleep
from betting.setup_driver import setup_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.safari.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
import time
from logger.bet_logger import setup_logger

logger = setup_logger('ifortuna')


class IFortuna():
    base_link = 'https://live.ifortuna.sk'

    def __init__(self) -> None:
        return
    
    def __str__(self) -> str:
        return 'IFortuna'

    def find_event(self, event: str) -> dict:
        logging.info(f'{self.__str__()}: Finding event {event}.')
        driver = setup_driver()
        driver.get(self.base_link)
        try:
            result_count = self._find_similar_events(driver, event)
            img_path = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaFindEvent.png'
            driver.save_screenshot(img_path)
            logger.info(f'{self.__str__()}: Found similar events.')
            return {'event_img': img_path, 'result_count': result_count}
        except Exception as e:
            logger.info(f'{self.__str__()}: Similar events not found.')
            exception_img = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaFindEventException.png'
            driver.save_screenshot(exception_img)
            return create_bet_exception_report(
                EventNotFoundException(
                    self.__str__(), 
                    event, 
                    exception_img, 
                    str(e)
                )    
            )
        finally:
            driver.close()

    def _find_similar_events(self, driver: WebDriver, event: str) -> int:
        self._search_for_event(driver, event)
        wait_for_search = WebDriverWait(driver, 0.5, 0.1)
        similar_events = wait_for_search.until(ec.presence_of_all_elements_located((By.XPATH, '//*[@id="app"]//div' + 
            '[@class="fortuna_search_bar__running fortuna_search_bar_matches"]/div[a[@class="fortuna_search_bar_matches__match_info_wrapper"]]')))
        return len(similar_events)
    
    def bet(self, account: dict, bet_info: dict, search_position: int) -> dict:
        event = bet_info['event']
        logger.info(f'{self.__str__()}: Betting event {event}...')
        try:
            driver = setup_driver()
            driver.get(self.base_link)
            self._login(driver, account['name'], account['password'])
            self._wait_for_popup_close(driver)
            self._navigate_to_event(driver, bet_info, search_position)
            translated_bet = self.translate_bet(bet_info)
            confirmation_img, bet_rate = self._place_bet(driver, translated_bet, account['bet_amount'])
            bet_report = create_bet_result_report(translated_bet, account, bet_rate, confirmation_img)
            self._logout(driver)
            return bet_report
        except BetTimeoutException as bte:
            return create_bet_exception_report(bte)
        except Exception as e:
            logger.info(f'{self.__str__()}: Runtime exception occured. exception: {e}')
            exception_img = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaBetRuntimeException.png'
            driver.save_screenshot(exception_img)
            return create_bet_exception_report(
                BetRuntimeException(
                    self.__str__(), 
                    bet_info['event'], 
                    exception_img, 
                    str(e)
                )
            )
        finally:
            logger.info(f'{self.__str__()}: Betting on event {event} ended.')
            driver.close()

    def translate_bet(self, bet_info: dict) -> dict:
        return {
            'event': bet_info['event'],
            'bet': BROKER_COMMANDS[self.__str__()][bet_info['bet']],
            'specs': self.translate_specs(bet_info),
            'sport': bet_info['sport'],
            'home': bet_info['home'],
            'away': bet_info['away']
        }

    def translate_specs(self, bet_info: dict) -> str:
        group = bet_info['bet']
        specs = bet_info['specs']
        if group == 'goly':
            value = specs[1:]
            if specs[0] == '+':
                return f'Viac ako ({value})'
            return f'Menej ako ({value})'
        elif group == 'handicap':
            team, value = specs.split('|')
            if team == '1':
                return bet_info['home'] + f' ({value})'
            return bet_info['away'] + f' ({value})'        
        elif group == 'vysledok':
            if specs == '1':
                return bet_info['home']
            elif specs == '2':
                return bet_info['away'] 
            else:
                return 'Rem??za'
        else:
            print('pruser v translate')
            raise Exception

    def _wait_for_popup_close(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Waiting for popup close...')
        wait_for_popup_close = WebDriverWait(driver, 20, 0.1)
        wait_for_popup_close.until(ec.presence_of_element_located(
            (By.XPATH, '//div[@class="simple_modal simple_modal--hidden simple_modal--with_overlay ' + 
            'simple_modal--default  user-message user-message--show user-message__centered  responsible-gaming"]')))

    def _send_keys_reliably(self, input_field, keys: str) -> None:
        while input_field.get_property('value') != keys:
            input_field.clear()
            for key in keys:
                input_field.send_keys(key)

    def _login(self, driver: WebDriver, login_name: str, password: str) -> None:
        logger.info(f'{self.__str__()}: Logging in...')
        wait_for_login_button = WebDriverWait(driver, 3)
        login_banner = wait_for_login_button.until(ec.visibility_of_element_located(
            (By.XPATH, '//*[@id="app"]//div[normalize-space(text())="Prihl??si??"]'))
        )
        login_banner.click()
        wait_login_form = WebDriverWait(driver, 2)
        login_name_field = wait_login_form.until(ec.visibility_of_element_located(
            (By.XPATH, '//*[@id="app"]//input[@name="username"]'))
        )
        password_field = driver.find_element_by_xpath('//*[@id="app"]//input[@name="password"]')
        self._send_keys_reliably(login_name_field, login_name)
        self._send_keys_reliably(password_field, password)
        login_button = driver.find_element_by_xpath('//*[@id="app"]//button[normalize-space(text())="Prihl??si??"]')
        login_button.click()

    def _navigate_to_event(self, driver: WebDriver, bet_info: dict, search_position: int) -> None:
        logger.info(f'{self.__str__()}: Navigating to event...')
        self._search_for_event(driver, bet_info['event'])
        wait_for_search = WebDriverWait(driver, 0.5, 0.1)
        try:
            search_element_xpath = '//*[@id="app"]//div[@class="fortuna_search_bar__running fortuna_search_bar_matches"]' + \
                f'/div[{search_position}]/a[@class="fortuna_search_bar_matches__match_info_wrapper"]'
            search_result = wait_for_search.until(ec.visibility_of_element_located(
                (By.XPATH, search_element_xpath)))
            bet_info['home'] = driver.find_element_by_xpath(search_element_xpath + '/div/div[1]').get_attribute('title')
            bet_info['away'] = driver.find_element_by_xpath(search_element_xpath + '/div/div[2]').get_attribute('title')
            search_result.click()

        except:
            raise Exception(f'Event name can be wrong, or this event is not available at {self.__str__()} broker.')

    def _search_for_event(self, driver: WebDriver, event: str) -> None:
        logger.info(f'{self.__str__()}: Searching for event...')
        search_field_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="view-menu__search-wrapper"]/button')
        search_field_button.click()
        wait_for_search_field = WebDriverWait(driver, 2)
        search_field = wait_for_search_field.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="search-input"]')))
        parsed_event = event.split('|')
        self._send_keys_reliably(search_field, parsed_event[0])

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> Tuple[str, float]:
        logger.info(f'{self.__str__()}: placing bet...')
        bet_xpath, bet_rate_xpath = self._create_ticket_xpaths(bet_info)
        time_now = time.time()
        timeout = time_now + BET_WAIT_TIME       
        ticket_denied_count = 0
        while time_now <= timeout:
            if self._bet_is_bettable(driver, bet_xpath, bet_rate_xpath):
                if self._process_ticket(driver, bet_xpath, bet_amount):
                    return self._process_ticket_approval(driver, bet_rate_xpath)
                ticket_denied_count += 1
                self._process_ticket_denial(driver, bet_info, bet_xpath, ticket_denied_count)
            logger.info(f'{self.__str__()}: One of the predicates failed, retrying...')
            time_now = time.time()
            sleep(1)
        logger.info(f'{self.__str__()}: Bet timedout...')
        raise BetTimeoutException(
            self.__str__(), 
            bet_info['event'], 
            '', 
            'Bet did not meet standards in time.'
        )

    def _create_ticket_xpaths(self, bet_info: dict) -> Tuple[str, str, str]:
        bet_xpath = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + \
            bet_info['specs'] + '"]'
        bet_rate_xpath = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + \
            bet_info['specs'] + '"]/span[@class="odds_button__value"]/span'
        return bet_xpath, bet_rate_xpath

    def _bet_is_bettable(self, driver: WebDriver, bet_xpath: str, bet_rate_xpath: str) -> bool:
        try:
            return self._bet_visible(driver, bet_xpath) and \
                   self._bet_unlocked_good_rate(driver, bet_rate_xpath)
        except:
            return False
    
    def _bet_visible(self, driver: WebDriver, bet_xpath: str) -> bool:
        logger.info(f'{self.__str__()}: checking visiility...')
        driver.find_element(By.XPATH, bet_xpath)
        return True

    def _bet_unlocked_good_rate(self, driver: WebDriver, bet_rate_xpath: str) -> bool:
        logger.info(f'{self.__str__()}: checking lock and rate...')
        bet_elements = driver.find_element(By.XPATH, bet_rate_xpath)
        return float(bet_elements.text.strip()) >= MIN_BET_RATE

    def _select_bet(self, driver: WebDriver, bet_xpath: str, log_prefix: str = '') -> None:
        logger.info(f'{self.__str__()}: {log_prefix}selecting bet...')
        bet_button = driver.find_element(By.XPATH, bet_xpath)
        driver.execute_script("arguments[0].scrollIntoView();", bet_button)
        bet_button.click()

    def _deselect_bet(self, driver: WebDriver, bet_xpath: str) -> None:
        self._select_bet(driver, bet_xpath, log_prefix='de')

    def _process_ticket(self, driver: WebDriver, bet_xpath: str, bet_amount: int) -> bool:
        logger.info(f'{self.__str__()}: processing ticket...')
        try:
            self._select_bet(driver, bet_xpath)
            send_ticket_button = self._setup_ticket_form(driver, bet_amount)
            logger.info(f'{self.__str__()}: sending ticket...')
            send_ticket_button.click()
            return self._ticket_approved(driver)
        except:
            return False

    def _process_ticket_denial(self, driver: WebDriver, bet_info: dict, bet_xpath: str, deny_count: int) -> None:
        logger.info(f'{self.__str__()}: Ticket denied (bookie or exception, check screenshots)...')
        event = '_'.join(bet_info['event'].split('|'))
        driver.save_screenshot(f'./betting/brokers/ifortuna/data/ticket_denials/{event}_{deny_count}.png')
        self._deselect_bet(driver, bet_xpath)

    def _process_ticket_approval(self, driver: WebDriver, bet_rate_xpath: str) -> Tuple[str, float]:
        bet_rate = float(driver.find_element_by_xpath(bet_rate_xpath).text.strip())
        confirmation_img = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaBetConfirmation.png'
        driver.save_screenshot(confirmation_img)
        return confirmation_img, bet_rate

    def _ticket_approved(self, driver: WebDriver) -> bool:
        logger.info(f'{self.__str__()}: waiting for bookie\'s decision...')
        wait_for_submission = WebDriverWait(driver, BOOKIE_DECISION_WAIT, 0.3)
        wait_for_submission.until_not(ec.visibility_of_element_located((By.XPATH, 
            '//*[@id="app_ticket"]//div[@class="ticket_content__messages"]//span[@class="ticket_content__submission_text"]')))
        try:
            wait_for_decision = WebDriverWait(driver, 5, 0.1)
            wait_for_decision.until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="app_ticket"]//div[@class="alert_box__text" and normalize-space(text()) = "Tiket bol prijat??!"]')))
            return True
        except:
            return False
        
    def _setup_ticket_form(self, driver: WebDriver, bet_amount: int) -> WebElement:
        logger.info(f'{self.__str__()}: setting up the ticket...')
        wait_bet_window = WebDriverWait(driver, 3)
        amount_field = wait_bet_window.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app_ticket"]//div[@class="ticket_stake"]/input')))
        self._send_keys_reliably(amount_field, bet_amount)
        bet_button = driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_summary__submit"]/button')
        select_rate_change = Select(driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_header__odds_accept"]//select'))
        select_rate_change.select_by_value("UPWARD")
        # not sure about this ci to sposobuje doublespending alebo nie
        '''if bet_button.text.strip() == 'PRIJA?? ZMENY':
            bet_button.click()'''
        return bet_button   

    def _logout(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Logging out...')
        account_banner = driver.find_element_by_xpath('//*[@id="app"]//div[@class="user_panel__info_user_box"]')
        logout_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="user_panel__logout"]/button')
        actions = ActionChains(driver)
        actions.move_to_element(account_banner)
        actions.click(logout_button)
        actions.perform()


def create_bet_result_report(bet_info: dict, account: dict, 
                           bet_rate: float, confirmation_img: str) -> dict:
    return {
        **bet_info,
        'broker': 'IFortuna',
        'allocation': account['bet_amount'],
        'bet_rate': bet_rate,
        'possible_win': float(account['bet_amount']) * bet_rate,
        'confirmation_img': confirmation_img
    }

def create_bet_exception_report(exception: Exception) -> dict:
    return {
        'broker': exception.broker,
        'exception': exception
    }