from selenium import webdriver
from selenium.webdriver.safari.webdriver import WebDriver


def setup_driver() -> WebDriver:
    driver = webdriver.Safari()
    driver.set_window_size(1200, 800)
    driver.implicitly_wait(3)
    return driver