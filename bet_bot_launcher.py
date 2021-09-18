from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from betting.setup_driver import setup_driver
from my_discord.bot.dc_bot import Bet_dc_bot
from logging.config import fileConfig
from selenium.webdriver.support import expected_conditions as ec

''' Priklad: Sport\n x vs y \n na co stavit (napr: 'pocet golov')\n kolko (napr: 'menej ako (3)') '''

def run_test(base_link: str):
    driver = setup_driver()
    driver.get(base_link)
    try:
        _bet_visible(
            driver, 
            '//div[@id="sportbook-main-container"]//div[@class="od__table"]//div[div[span[@title="Počet gólov"]]]//div[span[normalize-space(text()) = "Viac ako 4.5"]]'
        )
        sleep(3)
        print('vissible preslo')
        _setup_ticket_form(driver, '1000')
        print('ticket setup preslo')
    except Exception as e:
        print(type(e))
        sleep(100)
    finally:
        driver.close()


def _send_keys_reliably(input_field, keys: str) -> None:
    while input_field.get_property('value') != keys:
        input_field.clear()
        for key in keys:
            input_field.send_keys(key)

def _setup_ticket_form(driver, bet_amount: int):
    #logger.info(f'{self.__str__()}: setting up the ticket...')
    wait_bet_window = WebDriverWait(driver, 3)
    amount_field = wait_bet_window.until(ec.presence_of_element_located(
        (By.XPATH, '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]//div[@class="ticket__stake"]/input')))
    print('found amount field')
    select_rate_change = driver.find_element_by_xpath(
        '//aside[@class="main__right is--scrollable mCustomScrollbar _mCS_17"]' + 
        '//div[@class="ticket__stake"]' +
        '//div[@class="ticket__bet-options uk-accordion"]/div[1]')
    print('found rate_change menu')
    select_rate_change.click()
    print('clicked rate_change menu')
    _send_keys_reliably(amount_field ,bet_amount)
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
    #driver.execute_script("arguments[0].scrollIntoView();", bet_button)
    print('scrolled to bet button')
    sleep(10)
    return bet_button 

def _bet_visible(driver, bet_xpath: str) -> bool:
    #logger.info(f'{self.__str__()}: checking visiility...')
    bet_button = driver.find_element(By.XPATH, bet_xpath)
    driver.execute_script("arguments[0].scrollIntoView();", bet_button)
    bet_button.click()
    return True

if __name__ == '__main__':
    bot = Bet_dc_bot()
    bot.run()
    #run_test('https://www.doxxbet.sk/sk/sportove-tipovanie/futbal/anglicko/premier-league?event=23066711&name=everton-vs-norwich-city')



'''
$bet
futbal 
Norwich|Watford
Počet gólov
Viac ako 4.5
'''