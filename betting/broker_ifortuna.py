from my_discord.bot.dc_bot import Bet_dc_bot
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.safari.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


# TODO:
#   + prerobit lokalizaciu elementov na stabilnejsie veci ako napriklad id
#   + prerobit sleep() volania na presenceOfElementLocated (vid internet)
#   + prejdi si kod zisti kde mozu nastat chyby a pacni tam try bloky nech to nespadne
#   + sprav cheatsheet pre zavadzanie prikazov a spravne nakonfiguruj pre kazdy sport kontrolu prikazov nech maju lepsi fedback
#   + discordove rozhranie sprav nech to vies testnut cez discord
#   + sprav Doxxbet


class IFortuna():
    base_link = 'https://live.ifortuna.sk'

    def __init__(self) -> None:
        return

    def is_right_bet(self, bot: Bet_dc_bot) -> bool:
        pass
    
    def bet(self, account: dict, bet_info: dict) -> None:
        driver = webdriver.Safari()
        driver.get(self.base_link)
        driver.set_window_size(1500,800)
        self._login(driver, account['name'], account['password'])
        self._navigate_to_event(driver, bet_info['event'])
        self._place_bet(driver, bet_info, account['bet_amount'])
        self._logout(driver)

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
        sleep(13)
        search_field_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="view-menu__search-wrapper"]/button')
        search_field_button.click()
        wait_for_search_field = WebDriverWait(driver, 2)
        search_field = wait_for_search_field.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="search-input"]')))
        self._send_keys_reliably(search_field, event)
        wait_for_search = WebDriverWait(driver, 2)
        try:
            search_result = wait_for_search.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app"]//div[@class="fortuna_search_bar__running fortuna_search_bar_matches"]/div[1]')))
            search_result.click()
        except:
            print('IFortuna error: event name')
            #raise Exception('IFortuna error: control over your event name, else this match is not available')
        

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> None:
        bet = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + bet_info['specs'] + '"]'
        wait_for_bet = WebDriverWait(driver, 1200)
        try:
            bet_button = wait_for_bet.until(ec.visibility_of_element_located((By.XPATH, bet)))
        except:
            print('Ifortuna error: bet not found after 20 minutes')
            return
        sleep(2) # for element to be clickable
        bet_button.click()
        wait_bet_window = WebDriverWait(driver, 3)
        amount_field = wait_bet_window.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="app_ticket"]//div[@class="ticket_stake"]/input')))
        self._send_keys_reliably(amount_field, bet_amount)
        bet_button = driver.find_element_by_xpath('//*[@id="app_ticket"]//div[@class="ticket_summary__submit"]/button')
        if bet_button.text.strip() == 'PRIJAŤ ZMENY':
            bet_button.click()
        bet_button.click()

    def _logout(self, driver: WebDriver) -> None:
        account_banner = driver.find_element_by_xpath('//*[@id="app"]//div[@class="user_panel__info_user_box"]')
        logout_button = driver.find_element_by_xpath('//*[@id="app"]//div[@class="user_panel__logout"]/button')
        actions = ActionChains(driver)
        actions.move_to_element(account_banner)
        actions.click(logout_button)
        actions.perform()

        