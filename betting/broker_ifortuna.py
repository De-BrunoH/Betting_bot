from time import sleep
from selenium.webdriver.safari import webdriver
from selenium.webdriver.safari.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains


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
    
    def bet(self, account: dict, bet_info: dict) -> None:
        driver = webdriver.Safari()
        driver.get(self.base_link)
        sleep(2)
        self._login(driver, account['name'], account['password'])
        # sleep for safebetting countdown
        sleep(14)
        self._navigate_to_event(driver, bet_info['event'])
        sleep(3)
        self._place_bet(driver, bet_info, account['bet_amount'])

    def _login(self, driver: WebDriver, login_name: str, password: str) -> None:
        login_banner = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[1]')
        login_banner.click()
        login_name_field = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[2]/div[1]/input')
        password_field = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[2]/div[2]/input')
        login_name_field.send_keys(login_name)
        password_field.send_keys(password)
        sleep(1)
        login_button = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[2]/div[3]/button')
        login_button.click()

    def _navigate_to_event(self, driver: WebDriver, event: dict) -> None:
        search_field_button = driver.find_element_by_xpath('//*[@id="app"]/div[2]/nav/div[1]/div[2]/div[1]/div/button')
        search_field_button.click()
        search_field = driver.find_element_by_xpath('//*[@id="search-input"]')
        search_field.send_keys(event)
        search_result = driver.find_element_by_xpath('//*[@id="app"]/div[2]/nav/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/div[1]/div')
        search_result.click()

    def _place_bet(self, driver: WebDriver, bet_info: dict, bet_amount: int) -> None:
        bet = '//div[div[normalize-space(text()) = "' + bet_info['bet'] + '"]]//a[@title = "' + bet_info['specs'] + '"]'
        bet_button = driver.find_element_by_xpath(bet)
        bet_button.click()
        # set amount and place
        sleep(2)
        amount_field = driver.find_element_by_xpath('//*[@id="app_ticket"]/div/div[2]/div/div/div/div[3]/div/input')
        amount_field.clear()
        amount_field.send_keys(bet_amount)
        # bet_placer = driver.find_elementby_xpath('//*[@id="app_ticket"]/div/div[2]/div/div/div/div[4]/button')
        # bet_placer.click()

    def _logout(self, driver: WebDriver) -> None:
        '''Zatial nefunkcne'''
        account_banner = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[2]/div')
        action = ActionChains(driver)
        action.move_to_element(account_banner)
        
        logout_button = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[5]/div[3]/button')
        logout_button.click()


        