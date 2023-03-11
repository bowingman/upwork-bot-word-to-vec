import os
import time
import random
import importlib
from os import listdir
from os.path import isfile, join
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from create_email import get_verification_email, get_email_count
from utils import wait_till_page_loaded

config = importlib.import_module("config")


def next_step(driver):
    prev_url = driver.current_url
    driver.find_element(
        By.CSS_SELECTOR, "button[data-test='step-next-button']").click()
    while prev_url == driver.current_url:
        pass
    print(driver.current_url)


def set_settings(driver):
    driver.get('https://www.upwork.com/ab/messages/rooms/messages-settings-modal?sidebar=true&pageTitle=Messages%20Settings&_modalInfo=%5B%7B%22navType%22%3A%22modal%22,%22title%22%3A%22Messages%20Settings%22,%22modalId%22%3A%221673489957833%22,%22channelName%22%3A%22messages-settings%22%7D%5D')
    wait_till_page_loaded(driver)
    try:
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Continue')]").click()
        time.sleep(1)
        input = driver.find_element(
            By.CSS_SELECTOR, "input[data-test-id='anti-scam-acknowledge-checkbox']")
        input.find_element(By.XPATH, "./..").click()
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Done')]").click()
    except:
        pass
    time.sleep(2)
    try:
        driver.find_element(
            By.XPATH, "//span[contains(text(), 'Every 15 minutes')]/../..").click()
        driver.find_element(
            By.XPATH, "//span[contains(text(), 'Immediate')]/../..").click()
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Save')]"
        ).click()
    except:
        pass
    time.sleep(2)


def set_skill(driver, skills):
    error_flag = True
    while error_flag:
        error_flag = False
        try:
            driver.find_element(
                By.CSS_SELECTOR, '[class="up-typeahead-input-fake up-input"]').click()
            time.sleep(5)
        except:
            error_flag = True
            driver.get("https://www.upwork.com/nx/create-profile/skills")
            time.sleep(5)
            break
        for skill_name in skills:
            try:
                skill_input_combo = driver.find_element(
                    By.CSS_SELECTOR, "input[placeholder='Start typing to search for skills']")
                skill_input_combo.send_keys(Keys.ARROW_DOWN, Keys.RETURN)
                skill_input_combo.send_keys(skill_name)
                driver.find_element(
                    By.XPATH, f"//strong[contains(text(), '{skill_name}')]").click()
            except Exception as e:
                print(e)
                error_flag = True
                driver.get("https://www.upwork.com/nx/create-profile/skills")
                time.sleep(5)
                break


def sign_up_upwork(driver, email, dataBase, db_cursor):
    driver.get("https://www.upwork.com")
    driver.implicitly_wait(10)

    def create_account(driver):
        if driver.current_url != "https://www.upwork.com" and driver.current_url != "https://www.upwork.com/":
            return
        driver.get("https://www.upwork.com/nx/signup/?dest=home")
        driver.find_element(By.CSS_SELECTOR, '[data-qa="work"]').click()
        driver.find_element(By.CSS_SELECTOR, '[data-qa="btn-apply"]').click()
        first_name_element = driver.find_element(
            By.CSS_SELECTOR, '[placeholder="First name"]')
        first_name_element.clear()
        first_name_element.send_keys(config.first_name)
        last_name_element = driver.find_element(
            By.CSS_SELECTOR, '[placeholder="Last name"]')
        last_name_element.clear()
        last_name_element.send_keys(config.last_name)
        email_element = driver.find_element(
            By.CSS_SELECTOR, '[placeholder="Email"]')
        email_element.clear()
        email_element.send_keys(email)
        password_element = driver.find_element(By.ID, 'password-input')
        password_element.clear()
        password_element.send_keys(config.password)
        driver.find_element(By.CSS_SELECTOR, '[class="up-checkbox"]').click()
        prev_url = driver.current_url
        prev_email_count = get_email_count()
        driver.find_element(By.ID, 'button-submit-form').click()
        time.sleep(10)

        if prev_url == driver.current_url:
            print("Log in Failed!")
            return

        email_verification_url = False
        max_count, verification_count = 10, 0

        while email_verification_url == False and verification_count < max_count:
            while prev_email_count == get_email_count():
                time.sleep(2)
            email_verification_url = get_verification_email(prev_email_count)
            verification_count += 1
        driver.get(email_verification_url)
        print("Email Verified")
        time.sleep(10)
        return True

    def prepare_profile(driver):
        if driver.current_url == "https://www.upwork.com/nx/create-profile/welcome":
            driver.find_element(
                By.XPATH, '//span[contains(text(), "Get started")]').click()
            time.sleep(2)
        if driver.current_url == "https://www.upwork.com/nx/create-profile/experience":
            driver.find_element(
                By.CSS_SELECTOR, '[data-cy="button-box"]').click()
            time.sleep(2)
        if driver.current_url == "https://www.upwork.com/nx/create-profile/goal":
            driver.find_element(
                By.CSS_SELECTOR, '[data-cy="button-box"]').click()
            time.sleep(2)
        if driver.current_url == "https://www.upwork.com/nx/create-profile/work-preference":
            driver.find_element(
                By.CSS_SELECTOR, '[data-cy="button-box"]').click()
            time.sleep(1)
            driver.find_element(
                By.CSS_SELECTOR, '[class="mb-20 col-12 up-checkbox"]').click()
            driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            driver.find_element(
                By.XPATH, '//button[contains(text(), "Next, Create a Profile")]').click()
            time.sleep(10)

        return True

    def make_profile(driver):
        print(driver.current_url)
        if driver.current_url == "https://www.upwork.com/nx/create-profile/resume-import":
            driver.find_element(
                By.XPATH, "//button[contains(text(), 'Upload Your Resume')]").click()
            file_upload = driver.find_element(
                By.XPATH, "//input[@type='file']")
            file_upload.send_keys(
                config.profile_root_path + config.resume_file_name)

            while (True):
                try:
                    continue_btn = driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Continue')]")
                    if not continue_btn.get_attribute("disabled"):
                        continue_btn.click()
                        break
                except:
                    pass

        if driver.current_url == "https://www.upwork.com/nx/create-profile/title":
            title_element = driver.find_element(
                By.CSS_SELECTOR, "input[aria-labelledby='title-label']")
            title_element.clear()
            title_element.send_keys(config.profile_title)
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/employment":
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/education":
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/languages":
            try:
                driver.find_element(
                    By.CSS_SELECTOR, "[data-test='dropdown-toggle']").click()
                driver.find_element(
                    By.XPATH, "//span[contains(text(), '" + config.english_level + "')]").click()
            except:
                pass
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/skills":
            set_skill(driver, config.skills)
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/overview":
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/categories":
            try:
                category_elements = driver.find_elements(
                    By.CSS_SELECTOR, "div[class='up-skill-badge']")
                for i in range(len(category_elements)):
                    category_elements[i].find_element(
                        By.TAG_NAME, "button").click()
            except:
                input('Press Enter after select the Categories')
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/rate":
            element = driver.find_element(
                By.CSS_SELECTOR, "[data-test='hourly-rate']").find_element(By.TAG_NAME, "input")
            element.clear()
            element.send_keys(str(config.hourly_rate))
            next_step(driver)

        if driver.current_url == "https://www.upwork.com/nx/create-profile/location":
            while True:
                try:
                    driver.find_element(
                        By.CSS_SELECTOR, "div[data-test='dropdown-toggle']").click()
                    time.sleep(2)
                    country_ele = driver.find_element(
                        By.XPATH, "//span[contains(text(), '" + config.vps_location_country + "')]/../..")
                    time.sleep(1)
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", country_ele)
                    driver.find_element(
                        By.XPATH, "//span[contains(text(), '" + config.country + "')]/../..").click()
                    time.sleep(2)
                    driver.find_element(
                        By.CSS_SELECTOR, "input[aria-labelledby='street-label']").clear()
                    driver.find_element(
                        By.CSS_SELECTOR, "input[aria-labelledby='street-label']").send_keys(config.street)
                    time.sleep(1)
                    driver.find_element(By.CSS_SELECTOR, "div[data-test='input-city']").find_element(
                        By.TAG_NAME, "input").clear()
                    time.sleep(3)
                    driver.find_element(By.CSS_SELECTOR, "div[data-test='input-city']").find_element(
                        By.TAG_NAME, "input").send_keys(config.city)
                    # for i in range(len(config.city)):
                    #     driver.find_element(By.CSS_SELECTOR, "div[data-test='input-city']").find_element(
                    #         By.TAG_NAME, "input").send_keys(config.city[i])
                    #     time.sleep(1)
                    time.sleep(15)
                    driver.find_element(
                        By.CSS_SELECTOR, "div[data-test='input-city']").find_element(By.TAG_NAME, "li").click()
                    time.sleep(2)
                    driver.find_element(
                        By.CSS_SELECTOR, "input[data-test='zip']").clear()
                    driver.find_element(
                        By.CSS_SELECTOR, "input[data-test='zip']").send_keys(config.zip_code)
                    driver.find_element(
                        By.CSS_SELECTOR, "input[placeholder='Enter number']").clear()
                    driver.find_element(
                        By.CSS_SELECTOR, "input[placeholder='Enter number']").send_keys(config.phonenumber)
                    driver.find_element(
                        By.CSS_SELECTOR, "button[data-cy='open-loader']").click()
                    driver.find_element(By.CSS_SELECTOR, "span[data-test='select-image-select-button']").find_element(
                        By.TAG_NAME, 'input').send_keys(config.profile_root_path + config.avatar_file_name)
                    time.sleep(8)
                    driver.find_element(
                        By.CSS_SELECTOR, "button[data-test='select-image-save-button']").click()
                    time.sleep(15)
                    driver.find_element(
                        By.CSS_SELECTOR, "button[data-test='step-next-button']").click()
                    time.sleep(10)
                    break
                except Exception as e:
                    driver.get("https://www.upwork.com/nx/create-profile/location")
                    print(e)
                    pass

        if driver.current_url == "https://www.upwork.com/nx/create-profile/submit":
            driver.find_element(
                By.XPATH, "//span[contains(text(), 'Submit Profile')]").click()
            time.sleep(10)

        return True

    create_account(driver)
    prepare_profile(driver)
    make_profile(driver)
    set_settings(driver)
    return True, "You created a new account successfully!"


if __name__ == '__main__':
    sign_up_upwork()
