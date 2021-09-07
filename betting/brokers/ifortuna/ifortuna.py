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
            sleep(1)
            self._navigate_to_event(driver, event)
            sleep(2)
            img_path = './betting/brokers/ifortuna/data/tmp_screenshots/IFortunaFindEvent.png'
            driver.save_screenshot(img_path)
            return {'event_img': img_path}
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
    
    def bet(self, account: dict, bet_info: dict) -> dict:
        try:
            driver = setup_driver()
            driver.get(self.base_link)
            self._login(driver, account['name'], account['password'])
            sleep(13)
            self._navigate_to_event(driver, bet_info['event'])
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

    def _navigate_to_event(self, driver: WebDriver, event: str) -> None:
        search_field_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="view-menu__search-wrapper"]/button')
        search_field_button.click()
        wait_for_search_field = WebDriverWait(driver, 2)
        search_field = wait_for_search_field.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="search-input"]')))
        parsed_event = event.split('|')
        self._send_keys_reliably(search_field, parsed_event[0])
        wait_for_search = WebDriverWait(driver, 2)
        try:
            search_result = wait_for_search.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app"]//div[@class="fortuna_search_bar__running fortuna_search_bar_matches"]/div[1]/a[@class="fortuna_search_bar_matches__match_info_wrapper"]')))
            search_result.click()
        except:
            raise Exception(f'Event name can be wrong, or this event is not available at {self.__str__()} broker.')

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> Tuple[str, float]:
        bet = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + bet_info['specs'] + '"]'
        wait_for_bet = WebDriverWait(driver, BET_WAIT_TIME)
        try:
            bet_button = wait_for_bet.until(ec.visibility_of_element_located((By.XPATH, bet)))
        except:
            print(f'Bet not found after {BET_WAIT_TIME // 60} minutes.')
            return
        bet_rate = float(driver.find_element_by_xpath(bet + '/span[@class="odds_button__value"]/span').text)
        sleep(2) # for element to be clickable
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

        