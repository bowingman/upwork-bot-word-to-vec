import os
import time
import importlib
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from utils import wait_till_page_loaded

config = importlib.import_module("config")


def sign_in_upwork(driver, email, password):
    driver.get("https://www.upwork.com")
    driver.implicitly_wait(10)
    prev_url = driver.current_url
    if prev_url == "https://www.upwork.com/nx/find-work/best-matches":
        return True, "Already Signed!"
    if prev_url != "https://www.upwork.com/":
        return False, "Not corrected URL"
    driver.find_element(By.XPATH, "//a[contains(text(), 'Log In')]").click()
    email_input = driver.find_element(By.ID, 'login_username')
    email_input.clear()
    email_input.send_keys(email)
    email_input.clear()
    email_input.send_keys(email)
    driver.find_element(By.ID, 'login_password_continue').click()

    while (True):
        try:
            pass_input = driver.find_element(By.ID, 'login_password')
            pass_input.clear()
            pass_input.send_keys(password)
            login_btn = driver.find_element(
                By.ID, 'login_control_continue').click()
            break
        except StaleElementReferenceException:
            pass

    return True, "You signed in successfully!"


if __name__ == '__main__':
    sign_in_upwork()
