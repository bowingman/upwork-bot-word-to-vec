import time
import imaplib
import email
import importlib
from selenium.webdriver.common.by import By
from utils import create_drive_with_port, wait_till_page_loaded

config = importlib.import_module("config")


def create_new_email(name="Joseph"):
    email = ""
    driver = create_drive_with_port(
        port=8901, data_dir=config.anonaddy_chrome_path)
    driver.get("https://app.anonaddy.com/")
    if driver.current_url == "https://app.anonaddy.com/login":
        driver.find_element(By.ID, "username").send_keys(
            config.anonaddy_username)
        driver.find_element(By.ID, "password").send_keys(
            config.anonaddy_password)
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Login')]").click()
    wait_till_page_loaded(driver)
    time.sleep(1)
    driver.find_element(
        By.XPATH, "//button[contains(text(), 'Create New Alias')]").click()
    driver.find_element(By.ID, "alias_domain").send_keys(
        config.anonaddy_username + ".anonaddy.me")
    driver.find_element(By.ID, "alias_description").send_keys(f"Upwork {name}")
    driver.find_element(By.CSS_SELECTOR, "div[class='multiselect']").click()
    driver.find_element(
        By.ID, "alias_recipient_ids-multiselect-options").find_element(By.TAG_NAME, "li").click()
    driver.find_element(
        By.XPATH, "//button[contains(text(), 'Create Alias')]").click()
    time.sleep(3)
    block = driver.find_element(
        By.CSS_SELECTOR, "span[class='block']").find_element(By.TAG_NAME, "span")
    email = block.find_elements(By.TAG_NAME, 'span')[
        0].text + block.find_elements(By.TAG_NAME, 'span')[1].text

    return email


def get_verification_email_from_inbox(email_message):
    email_content = email_message.get_payload()[1].get_payload()
    token = email_content.split(
        'Verify Email')[-2].split('/')[-1].split('">')[0]

    return f"https://www.upwork.com/signup/verify-email/token/{token}"


def is_upwork_verification_email(email_message):
    if email_message["Subject"] == "Verify your email address" and \
            email_message["From"].split('\r\n')[0] == '"donotreply at upwork.com"':
        return True
    return False


def get_email_count():
    user = config.primary_gmail
    password = config.gmail_key
    my_mail = imaplib.IMAP4_SSL("imap.gmail.com")
    my_mail.login(user, password)
    my_mail.select('Inbox')
    status, messages = my_mail.search(None, 'ALL')
    message_ids = messages[0].split()
    count = len(message_ids) - 1
    return count


def get_verification_email(prev_count):
    user = config.primary_gmail
    password = config.gmail_key
    my_mail = imaplib.IMAP4_SSL("imap.gmail.com")
    my_mail.login(user, password)
    my_mail.select('Inbox')
    status, messages = my_mail.search(None, 'ALL')
    message_ids = messages[0].split()
    count = len(message_ids) - 1
    while True:
        for i in range(count, prev_count, -1):
            email_id = message_ids[i]
            status, data = my_mail.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            if is_upwork_verification_email(email_message):
                verification_email = get_verification_email_from_inbox(
                    email_message)
                my_mail.close()
                my_mail.logout()
                return verification_email
