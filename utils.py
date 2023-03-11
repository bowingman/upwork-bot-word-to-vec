import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_drive(host="localhost:8989", wait_time=10):
    opt = Options()
    opt.add_experimental_option('debuggerAddress', host)
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=opt)
    driver.implicitly_wait(10)

    return driver

def create_drive_with_port(port=8999, data_dir="C:\\Users\\Administrator\\Desktop\\Selenium\\SeleniumDrivers\\ChromeYYY"):
    chrome_options = Options()
    chrome_options.add_argument(f'--remote-debugging-port={port}')
    chrome_options.add_argument(f'--user-data-dir={data_dir}')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(1300, 1000)
    driver.implicitly_wait(10)

    return driver

def wait_till_page_loaded(driver):
    while True:
        ready_state = driver.execute_script('return document.readyState;')
        if ready_state == 'complete':
            break

    return "Successfully Loaded!"


def delete_cache(driver):
    driver.get("https://www.upwork.com")
    time.sleep(30)
    driver.execute_script('window.localStorage.clear()')
    driver.execute_script('window.sessionStorage.clear()')

    for i in range(10):
        driver.delete_all_cookies()
        time.sleep(2)

    driver.get("about:blank")
    time.sleep(5)
