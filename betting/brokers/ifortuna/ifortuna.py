from betting.better.better_config import BET_WAIT_TIME
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


class IFortuna():
    base_link = 'https://live.ifortuna.sk'

    def __init__(self) -> None:
        return
    
    def __str__(self) -> str:
        return 'IFortuna'

    def find_event(self, event: str) -> str:
        driver = setup_driver()
        driver.get(self.base_link)
        try:
            result_count = self._find_similar_events(driver, event)
            img_path = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaFindEvent.png'
            driver.save_screenshot(img_path)
            return {'event_img': img_path, 'result_count': result_count}
        except Exception as e:
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
    
    def bet(self, account: dict, bet_info: dict, search_position: int) -> dict:
        try:
            driver = setup_driver()
            driver.get(self.base_link)
            self._login(driver, account['name'], account['password'])
            wait_for_popup_close = WebDriverWait(driver, 20, 0.1)
            wait_for_popup_close.until(ec.presence_of_element_located(
                (By.XPATH, '//div[@class="simple_modal simple_modal--hidden simple_modal--with_overlay ' + 
                'simple_modal--default  user-message user-message--show user-message__centered  responsible-gaming"]')))
            self._navigate_to_event(driver, bet_info['event'], search_position)
            confirmation_img, bet_rate = self._place_bet(driver, bet_info, account['bet_amount'])
            bet_report = create_bet_result_report(bet_info, account, bet_rate, confirmation_img)
            self._logout(driver)
            return bet_report
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
            driver.close()

    def _send_keys_reliably(self, input_field, keys: str) -> None:
        while input_field.get_property('value') != keys:
            input_field.clear()
            for key in keys:
                input_field.send_keys(key)

    def _login(self, driver: WebDriver, login_name: str, password: str) -> None:
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
        self._search_for_event(driver, event)
        wait_for_search = WebDriverWait(driver, 0.5, 0.1)
        try:
            search_result = wait_for_search.until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]//div[@class="fortuna_search_bar__running fortuna_search_bar_matches"]' + 
                f'/div[{search_position}]/a[@class="fortuna_search_bar_matches__match_info_wrapper"]')))
            search_result.click()
        except:
            raise Exception(f'Event name can be wrong, or this event is not available at {self.__str__()} broker.')

    def _find_similar_events(self, driver: WebDriver, event: str) -> int:
        self._search_for_event(driver, event)
        wait_for_search = WebDriverWait(driver, 0.5, 0.1)
        similar_events = wait_for_search.until(ec.presence_of_all_elements_located((By.XPATH, '//*[@id="app"]//div' + 
            '[@class="fortuna_search_bar__running fortuna_search_bar_matches"]/div[a[@class="fortuna_search_bar_matches__match_info_wrapper"]]')))
        return len(similar_events)

    def _search_for_event(self, driver: WebDriver, event: str) -> None:
        search_field_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="view-menu__search-wrapper"]/button')
        search_field_button.click()
        wait_for_search_field = WebDriverWait(driver, 2)
        search_field = wait_for_search_field.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="search-input"]')))
        parsed_event = event.split('|')
        self._send_keys_reliably(search_field, parsed_event[0])
            

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> Tuple[str, float]:
        bet = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + bet_info['specs'] + '"]'
        wait_for_bet = WebDriverWait(driver, BET_WAIT_TIME)
        try:
            bet_button = wait_for_bet.until(ec.visibility_of_element_located((By.XPATH, bet)))
        except:
            print(f'Bet not found after {BET_WAIT_TIME // 60} minutes.')
            return
        bet_rate = float(driver.find_element_by_xpath(bet + '/span[@class="odds_button__value"]/span').text)
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
        return confirmation_img, bet_rate

    def _bet_is_locked(self, driver: WebDriver, bet_xpath: str) -> bool:
        
            driver.find_element_by_xpath(bet_xpath + '/span[@class="odds_button__value"]/div[@class="icon icon--lock icon--size_auto"]')

    def _logout(self, driver: WebDriver) -> None:
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