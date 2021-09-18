import logging
from betting.bet_exceptions.BetTimeoutException import BetTimeoutException
from selenium.webdriver.safari import webdriver
from betting.better.better_config import BET_WAIT_TIME, BOOKIE_DECISION_WAIT, MIN_BET_RATE
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

logger = setup_logger('doxxbet')

class Doxxbet():
    base_link = 'https://www.doxxbet.sk/sk/live-tipovanie'

    def __init__(self) -> None:
        return

    def __str__(self) -> str:
        return 'Doxxbet'

    def find_event(self, event: str) -> dict:
        logger.info(f'{self.__str__()}: Finding event {event}.')
        driver = setup_driver()
        driver.get(self.base_link)
        try:
            result_count = self._find_similar_events(driver, event)
            img_path = './betting/brokers/doxxbet/data/tmp_screenshots/DoxxbetFindEvent.png'
            driver.save_screenshot(img_path)
            logger.info(f'{self.__str__()}: Found similar events.')
            return {'event_img': img_path, 'result_count': result_count}
        except Exception as e:
            logger.info(f'{self.__str__()}: Similar events not found.')
            exception_img = './betting/brokers/doxxbet/data/tmp_screenshots/DoxxbetFindEventException.png'
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
        similar_events = wait_for_search.until(ec.presence_of_all_elements_located(
            (By.XPATH, '//aside[@id="modal-search"]//div[@id="mCSB_1_container"]/div/div/a')))
        return len(similar_events) if len(similar_events) <= 10 else 10
    
    def bet(self, account: dict, bet_info: dict, search_position: int) -> dict:
        event = bet_info['event']
        logger.info(f'{self.__str__()}: Betting event {event}...')
        try:
            driver = setup_driver()
            driver.get(self.base_link)
            self._login(driver, account['name'], account['password'])
            # v ifortuna nie je
            self._wait_for_login(driver)
            # =================
            self._wait_for_popup_close(driver)
            # v ifotuna nie je
            self._resolve_duplicate_login(driver)
            # =================
            self._navigate_to_event(driver, bet_info['event'], search_position)
            confirmation_img, bet_rate = self._place_bet(driver, bet_info, account['bet_amount'])
            bet_report = create_bet_result_report(bet_info, account, bet_rate, confirmation_img)
            '''self._logout(driver)'''
            print('done')
            sleep(30)
            return bet_report
        except BetTimeoutException as bte:
            return create_bet_exception_report(bte)
        except Exception as e:
            logger.info(f'{self.__str__()}: Runtime exception occured. exception: {e}')
            exception_img = './betting/brokers/doxxbet/data/tmp_screenshots/DoxxbetBetRuntimeException.png'
            driver.save_screenshot(exception_img)
            return create_bet_exception_report(
                BetRuntimeException(
                    self.__str__(), 
                    bet_info['event'], 
                    exception_img, 
                    str(type(e)) + ':' + str(e)
                )
            )
        finally:
            logger.info(f'{self.__str__()}: Betting on event {event} ended.')
            driver.close()

    def _send_keys_reliably(self, input_field, keys: str) -> None:
        while input_field.get_property('value') != keys:
            input_field.clear()
            for key in keys:
                input_field.send_keys(key)

    def _login(self, driver: WebDriver, login_name: str, password: str) -> None:
        logger.info(f'{self.__str__()}: Logging in...')
        wait_for_login_button = WebDriverWait(driver, 3)
        login_banner = wait_for_login_button.until(ec.visibility_of_element_located(
            (By.XPATH, '//header[@class="main__header main__header--sticked lng-switcher-hide"]//a[@href="#modal-login"]'))
        )
        login_banner.click()
        wait_login_form = WebDriverWait(driver, 2)
        login_name_field = wait_login_form.until(ec.visibility_of_element_located(
            (By.XPATH, '//aside[@id="modal-login"]//input[@id="modal-login-email"]'))
        )
        password_field = driver.find_element_by_xpath('//aside[@id="modal-login"]//input[@id="modal-login-password"]')
        self._send_keys_reliably(login_name_field, login_name)
        self._send_keys_reliably(password_field, password)
        login_button = driver.find_element_by_xpath('//aside[@id="modal-login"]//button[@id="login-submit-button"]')
        login_button.click()

    def _resolve_duplicate_login(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Resolving duplicate login...')
        try:
            wait = WebDriverWait(driver, 1.5, 0.1)
            close_button = wait.until(ec.presence_of_element_located(
                (By.XPATH, '//aside[@id="modal-standart"]//button[@class="uk-modal-close uk-close"]')))
            close_button.click()
            sleep(2) # wait fot slow javascript
        except:
            print('neni duplicate banner')
            return
        
    def _wait_for_login(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Waiting for login...')
        wait = WebDriverWait(driver, 10, 0.1)
        wait.until_not(ec.visibility_of_element_located(
            (By.XPATH, '//aside[@id="modal-login" and @style="display: block; overflow-y: scroll;"]')))

    def _wait_for_popup_close(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Waiting for popup close...')
        # v ifortuna nie je
        wait_for_popup_open = WebDriverWait(driver, 20, 0.1)
        wait_for_popup_open.until_not(ec.presence_of_element_located(
            (By.XPATH, '//aside[@id="casino-client-information-modal" and @style="display: none; overflow-y: scroll;"]')))
        # =================
        wait_for_popup_close = WebDriverWait(driver, 20, 0.1)
        wait_for_popup_close.until_not(ec.presence_of_element_located(
            (By.XPATH, '//aside[@id="casino-client-information-modal" and @style="display: block; overflow-y: scroll;"]')))
        

    def _navigate_to_event(self, driver: WebDriver, event: str, search_position: int) -> None:
        logger.info(f'{self.__str__()}: Navigating to event...')
        self._search_for_event(driver, event)
        try:
            # v ifortuna nie je
            search_results = driver.find_elements_by_xpath('//aside[@id="modal-search"]//a[@class="offer__row ng-scope"]')
            search_results[search_position - 1].click()
            # ================
        except Exception as e:
            print(e)
            raise Exception(f'Event name can be wrong, or this event is not available at {self.__str__()} broker.')

    def _search_for_event(self, driver: WebDriver, event: str) -> None:
        logger.info(f'{self.__str__()}: Searching for event...')
        search_field_button = driver.find_element_by_xpath(
            '//header[@class="main__header main__header--sticked lng-switcher-hide"]//div[@class="pull-right search-button cursor-pointer tooltipstered"]')
        search_field_button.click()
        wait_for_search_field = WebDriverWait(driver, 2)
        search_field = wait_for_search_field.until(ec.visibility_of_element_located(
            (By.XPATH, '//aside[@id="modal-search"]//input')))
        parsed_event = event.split('|')
        self._send_keys_reliably(search_field, parsed_event[0])
        # v ifortuna nebolo (aby bol lepsi screenshot)
        wait_for_result_display = WebDriverWait(driver, 5, 0.1)
        wait_for_result_display.until(ec.presence_of_element_located(
            (By.XPATH, '//aside[@id="modal-search"]//div[@class="search-result-group enable_animations"]')))
        # ==================

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
        bet_xpath = '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="' + bet_info['bet'] + \
            '"]]]//div[span[normalize-space(text()) = "' + bet_info['specs'] + '"]]'
        bet_rate_xpath = '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="' + bet_info['bet'] + \
            '"]]]//div[span[normalize-space(text()) = "' + bet_info['specs'] + '"]]//div[@class="odd-space"]/span[2]'
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
        driver.save_screenshot(f'./betting/brokers/doxxbet/data/ticket_denials/{event}_{deny_count}.png')
        self._deselect_bet(driver, bet_xpath)

    # prerobit ticket approval na citanie z toho banneru ked to prejde
    def _process_ticket_approval(self, driver: WebDriver, bet_rate_xpath: str) -> Tuple[str, float]:
        bet_rate = float(driver.find_element_by_xpath(bet_rate_xpath).text.strip())
        confirmation_img = './betting/brokers/doxxbet/data/tmp_screenshots/DoxxbetBetConfirmation.png'
        driver.save_screenshot(confirmation_img)
        return confirmation_img, bet_rate

    def _ticket_approved(self, driver: WebDriver) -> bool:
        logger.info(f'{self.__str__()}: waiting for bookie\'s decision...')
        wait_for_submission = WebDriverWait(driver, BOOKIE_DECISION_WAIT, 0.3)
        wait_for_submission.until_not(ec.presence_of_element_located((By.XPATH, 
            '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_25"]' + 
            '//div[@ng-controller="TicketController as tc"]' +
            '//div[@ng-if="tc.ticketSyncing"]')))
        try:
            wait_for_decision = WebDriverWait(driver, 5, 0.1)
            wait_for_decision.until(ec.presence_of_element_located((By.XPATH, 
                '//aside[@id="modal-ticket" and @style="display: block; overflow-y: scroll;"]' + 
                '//span[normalize-space(text()) = Schválený]')))
            print('prijaty')
            return True
        except:
            print('neprijaty')
            return False
        
    def _setup_ticket_form(self, driver: WebDriver, bet_amount: int) -> WebElement:
        logger.info(f'{self.__str__()}: setting up the ticket...')
        print('setting up the ticket')
        wait_bet_window = WebDriverWait(driver, 3)
        amount_field = wait_bet_window.until(ec.visibility_of_element_located(
            (By.XPATH, '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]//div[@class="ticket__stake"]/input')))
        print('found amount field')
        select_rate_change = driver.find_element_by_xpath(
            '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]' +
            '//div[@class="ticket__stake"]//div[@class="ticket__bet-options uk-accordion"]/div[1]'
        )
        print('found rate_change menu')
        select_rate_change.click()
        print('clicked rate_change menu')
        self._send_keys_reliably(amount_field, bet_amount)
        only_higher_odds = driver.find_element_by_xpath(
            '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]' +
            '//div[@class="ticket__stake"]//div[contains(@class, "ticket__bet-options")]' +
            '//label[normalize-space(text()) = "Prijať len zmenu kurzu nahor"]'
        )
        print('found higher change')
        only_higher_odds.click()
        print('clicked higher change')
        bet_button = driver.find_element_by_xpath(
            '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]//div[@class="ticket__footer uk-vertical-align ng-scope"]/button')
        print('found bet button')
        driver.execute_script("arguments[0].scrollIntoView();", bet_button)
        print('scrolled to bet button')
        return bet_button   

    def _logout(self, driver: WebDriver) -> None:
        logger.info(f'{self.__str__()}: Logging out...')
        account_banner = driver.find_element_by_xpath('//div[@id="uk-dropdown-profile"]')
        logout_button = driver.find_element_by_xpath('///div[@id="logoutDiv"')
        account_banner.click()
        logout_button.click()


def create_bet_result_report(bet_info: dict, account: dict, 
                           bet_rate: float, confirmation_img: str) -> dict:
    return {
        **bet_info,
        'broker': 'Doxxbet',
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


