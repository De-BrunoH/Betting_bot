import logging
from betting.bet_exceptions.BetException import BetException
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
from logger.bet_logger import logger


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
                    broker=self.__str__(), 
                    event=event, 
                    screenshot_path=exception_img, 
                    root_message=str(e)
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
            self._navigate_to_event(driver, bet_info['event'], search_position)
            confirmation_img, bet_rate = self._place_bet(driver, bet_info, account['bet_amount'])
            bet_report = create_bet_result_report(bet_info, account, bet_rate, confirmation_img)
            self._logout(driver)
            return bet_report
        except (BetTimeoutException) as bte:
            return create_bet_exception_report(bte)
        except Exception as e:
            exception_img = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaBetRuntimeException.png'
            driver.save_screenshot(exception_img)
            return create_bet_exception_report(
                BetRuntimeException(
                    broker=self.__str__(), 
                    event=bet_info['event'], 
                    screenshot_path=exception_img, 
                    root_message=str(e)
                )
            )
        finally:
            logger.info(f'{self.__str__()}: Betting on event {event} ended.')
            driver.close()

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
        login_banner = wait_for_login_button.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app"]//div[normalize-space(text())="Prihlásiť"]')))
        login_banner.click()
        wait_login_form = WebDriverWait(driver, 2)
        login_name_field = wait_login_form.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app"]//input[@name="username"]')))
        password_field = driver.find_element_by_xpath('//*[@id="app"]//input[@name="password"]')
        self._send_keys_reliably(login_name_field, login_name)
        self._send_keys_reliably(password_field, password)
        login_button = driver.find_element_by_xpath('//*[@id="app"]//button[normalize-space(text())="Prihlásiť"]')
        login_button.click()

    def _navigate_to_event(self, driver: WebDriver, event: str, search_position: int) -> None:
        logger.info(f'{self.__str__()}: Navigating to event...')
        self._search_for_event(driver, event)
        wait_for_search = WebDriverWait(driver, 0.5, 0.1)
        try:
            search_result = wait_for_search.until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]//div[@class="fortuna_search_bar__running fortuna_search_bar_matches"]' + 
                f'/div[{search_position}]/a[@class="fortuna_search_bar_matches__match_info_wrapper"]')))
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
            

    '''def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> Tuple[str, float]:
        bet = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]'
        odds = '//a[@title = "' + bet_info['specs'] + '"]'
        wait_for_bet = WebDriverWait(driver, BET_WAIT_TIME)
        try:
            bet_button = wait_for_bet.until(ec.visibility_of_element_located((By.XPATH, bet + odds)))
        except:
            print(f'Bet not found after {BET_WAIT_TIME // 60} minutes.')
            return
        bet_rate = float(driver.find_element_by_xpath(bet + odds + '/span[@class="odds_button__value"]/span').text)
        bet_button.click()
        wait_bet_window = WebDriverWait(driver, 3)
        amount_field = wait_bet_window.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app_ticket"]//div[@class="ticket_stake"]/input')))
        self._send_keys_reliably(amount_field, bet_amount)
        bet_button = driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_summary__submit"]/button')
        if bet_button.text.strip() == 'PRIJAŤ ZMENY':
            bet_button.click()
        bet_button.click()
        sleep(1)
        confirmation_img = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaBetConfirmation.png'
        driver.save_screenshot(confirmation_img)
        return confirmation_img, bet_rate'''

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> Tuple[str, float]:
        logger.info(f'{self.__str__()}: placing bet...')
        bet_xpath, bet_lock_xpath, bet_rate_xpath = self._create_ticket_xpaths(bet_info)
        ticket_result = {}
        timeout = int(time.time() + BET_WAIT_TIME)
        ticket_denied_count = 0
        while time.time() <= timeout:
            if self._bet_visible(driver, bet_info, bet_xpath) and \
                  self._bet_unlocked(driver, bet_info, bet_lock_xpath) and \
                  self._bet_good_rate(driver, bet_info, bet_rate_xpath):
                if self._send_ticket(driver, bet_info, bet_xpath, bet_amount, ticket_result):
                    return ticket_result['confirmation_img'], ticket_result['bet_rate']
                else:
                    ticket_denied_count += 1
                    event = '_'.join(bet_info['event'].split('|'))
                    driver.save_screenshot(f'./betting/brokers/ifortuna/data/ticket_denials/{event}_{ticket_denied_count}.png')
            sleep(1)
            logger.info(f'{self.__str__()}: One of the predicates failed, retrying...')
        logger.info(f'{self.__str__()}: Bet timedout...')
        raise BetTimeoutException(
            broker=self.__str__(), 
            event=bet_info['event'], 
            screenshot_path='', 
            root_message='Bet did not meet standards in time. Or was denied by bookie see Ifortuna logs.'
        )

    def _create_ticket_xpaths(self, bet_info: dict) -> Tuple[str, str, str]:
        bet_xpath = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + \
            bet_info['specs'] + '"]'
        bet_lock_xpath = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + \
            bet_info['specs'] + '" and @class="odds_button odds_button--horizontal odds_button--locked"]'
        bet_rate_xpath = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + \
            bet_info['specs'] + '"]/span[@class="odds_button__value"]/span'
        return bet_xpath, bet_lock_xpath, bet_rate_xpath

    def _bet_visible(self, driver: WebDriver, bet_info: dict, bet_xpath: str) -> bool:
        logger.info(f'{self.__str__()}: checking visiility...')
        return 1 == len(driver.find_elements(By.XPATH, bet_xpath))

    def _bet_unlocked(self, driver: WebDriver, bet_info: dict, bet_lock_xpath: str) -> bool:
        logger.info(f'{self.__str__()}: checking lock...')
        return 0 == len(driver.find_elements(By.XPATH, bet_lock_xpath))

    def _bet_good_rate(self, driver: WebDriver, bet_info: dict, bet_rate_xpath: str) -> bool:
        logger.info(f'{self.__str__()}: checking rate...')
        bet_element = driver.find_elements(By.XPATH, bet_rate_xpath)
        return 1 == len(bet_element) and float(bet_element.text.strip()) >= MIN_BET_RATE

    def _send_ticket(self, driver: WebDriver, bet_info, bet_xpath: str, bet_amount: int, ticket_result: dict) -> bool:
        logger.info(f'{self.__str__()}: sending ticket...')
        try:
            send_ticket_button = self._setup_ticket_form(driver, bet_xpath, bet_amount)
            send_ticket_button.click()
            self._wait_for_bookie(driver)
            try:
                # checking for positive bookie message
                driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_content__messages"]//*[contains(text(), "Tiket bol prijatý")]')
            except:
                logger.info(f'{self.__str__()}: Ticket denied by bookie...')
                return False
        except:
            return False
        ticket_result['confirmation_img'] = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaBetConfirmation.png'
        driver.save_screenshot(ticket_result['confirmation_img'])
        ticket_result['bet_rate'] = float(driver.find_element_by_xpath('//*[@id="app_ticket"]//span[@class="ticket_winnings__item_value"]').text.strip())
        return True

    def _wait_for_bookie(self, driver) -> None:
        logger.info(f'{self.__str__()}: waiting for bookie\'s decision...')
        wait_for_bokie_decision = WebDriverWait(driver, BOOKIE_DECISION_WAIT, 0.1)
        wait_for_bokie_decision.until_not(ec.visibility_of_element_located((By.XPATH, 
            '//*[@id="app_ticket"]//div[@class="ticket_content__messages"]//span[@class="ticket_content__submission_text"]')))
        
    def _setup_ticket_form(self, driver: WebDriver, bet_xpath: str, bet_amount: int) -> WebElement:
        logger.info(f'{self.__str__()}: setting up the ticket...')
        bet = driver.find_elements(By.XPATH, bet_xpath)
        bet.click()
        wait_bet_window = WebDriverWait(driver, 3)
        amount_field = wait_bet_window.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app_ticket"]//div[@class="ticket_stake"]/input')))
        self._send_keys_reliably(amount_field, bet_amount)
        bet_button = driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_summary__submit"]/button')
        select_rate_change = Select(driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_header__odds_accept"]//select'))
        select_rate_change.select_by_value("UPWARD")
        if bet_button.text.strip() == 'PRIJAŤ ZMENY':
            bet_button.click()
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