from time import sleep
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains


class IFortuna():
    base_link = 'https://live.ifortuna.sk'

    def __init__(self) -> None:
        return
    
    def bet(self, driver: WebDriver, login_name: str, login_password: str, bet_info: dict) -> None:
        sleep(2)
        self._login(driver, login_name, login_password)
        # sleep for safebetting countdown
        sleep(14)
        self._navigate_to_event(driver, bet_info['event'])
        self._place_bet(driver, bet_info)
        # logout not working
        #self._logout(driver)

    def setup_broker(self, driver: WebDriver) -> None:
        driver.get(self.base_link)

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

    def _place_bet(self, driver: WebDriver, bet_info: dict) -> None:
        pass

    def _logout(self, driver: WebDriver) -> None:
        '''Zatial nefunkcne'''
        account_banner = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[2]/div')
        action = ActionChains(driver)
        action.move_to_element(account_banner)
        
        logout_button = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div/div/div[5]/div[3]/button')
        logout_button.click()