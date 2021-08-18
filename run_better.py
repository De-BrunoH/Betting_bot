from Better import Better
from typing import List
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
import discord

command = 'futbal\nVratimov\nZápas: počet gólov\nMenej ako (2.5)'

# FUTBAL
# banner vsetkych stavok
all_bets = '//*[@id="app"]/div[3]/div[3]/div/div[2]/div[2]/div[2]/div/div[2]/div[1]/section[1]'
# hlavne stavky
main_bets = all_bets + '/div[1]/div/div[2]/div'
# goly stavky
goal_bets = all_bets + '/div[2]/div/div[2]/div'

def run_better() -> None:
    driver = webdriver.Safari()
    driver.maximize_window()
    better = Better(driver)
    better.process_bet(command)
    driver.close()

run_better()