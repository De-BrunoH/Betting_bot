from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.safari.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from betting.setup_driver import setup_driver
from my_discord.bot.dc_bot import Bet_dc_bot
from logging.config import fileConfig
from selenium.webdriver.support import expected_conditions as ec

''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (3)') '''

def _create_ticket_xpaths(bet_info: dict):
    bet_xpath = '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="' + bet_info['bet'] + \
        '"]]]//div[span[normalize-space(text()) = "' + bet_info['specs'] + '"]]'
    bet_rate_xpath = '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="' + bet_info['bet'] + \
        '"]]]//div[span[normalize-space(text()) = "' + bet_info['specs'] + '"]]//div[@class="odd-space"]/span[2]'
    return bet_xpath, bet_rate_xpath

def _select_bet(driver, bet_xpath: str, log_prefix: str = '') -> None:
    bet_button = driver.find_element(By.XPATH, bet_xpath)
    print('found button and now scrolling')
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", bet_button)
    print('scrolled')
    print('now clicking')
    bet_button.click()
    print('clicked')

def _deselect_bet(driver:WebDriver, bet_xpath: str) -> None:
    bet_button = driver.find_element(By.XPATH, bet_xpath)
    print('found button and now scrolling')
    driver.execute_script("arguments[0].scrollIntoViewIfNeeded(true);", bet_button)
    print('scrolled')
    print('now declicking')
    bet_button.click()
    print('declicked')

def run_test(base_link: str):
    driver = setup_driver()
    driver.get(base_link)
    try:
        bet_xpath = '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="Kto dá 2. gól"]]]//div[span[normalize-space(text()) = "Shaanxi Changan"]]'
        print('selecting')
        _select_bet(driver, bet_xpath)
        print('selected')
        sleep(3)
        print('deselecting')
        _deselect_bet(driver, bet_xpath)
        print('deselected')
        sleep(100)
    except Exception as e:
        print(type(e))
        sleep(100)
    finally:
        driver.close()

if __name__ == '__main__':
    bot = Bet_dc_bot()
    bot.run()
    #run_test('https://www.doxxbet.sk/sk/live-tipovanie/futbal/cina?event=23214691&name=shaanxi-changan-vs-kunshan')



'''
$bet
futbal 
Flaminia
Počet gólov
Viac ako 1.5
'''