from selenium import webdriver
from selenium.webdriver.safari.webdriver import WebDriver


def setup_driver(self) -> WebDriver:
    driver = webdriver.Safari()
    driver.set_window_size(1200, 800)
    return driver