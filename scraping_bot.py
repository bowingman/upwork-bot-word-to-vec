import time
import json
import datetime
import importlib
import mysql.connector
from selenium.webdriver.common.by import By
from sign_in import sign_in_upwork
from utils import create_drive, delete_cache, wait_till_page_loaded

config = importlib.import_module("config")


def get_skills(element):
    res_skills = []
    try:
        skills_element = element.find_element(
            By.CSS_SELECTOR, "div[class='up-skill-wrapper']").find_elements(By.TAG_NAME, "a")
    except:
        return res_skills
    for skill in skills_element:
        res_skills.append(skill.text)

    return res_skills


def main(driver, dataBase, db_cursor):
    current_page = 1
    while current_page < 500:
        print("Page " + str(current_page))
        try:
            url = "https://www.upwork.com/nx/jobs/search/?sort=recency&category2_uid=531770282580668420,531770282580668418"
            if current_page == 1:
                driver.get(url)
            else:
                driver.get(url + "&page=" + str(current_page))
            wait_till_page_loaded(driver)
            job_lists = driver.find_element(
                By.CSS_SELECTOR, "div[data-test='job-tile-list']").find_elements(By.TAG_NAME, "section")
            print(len(job_lists), " jobs found")
            for i in range(len(job_lists)):
                job_id = job_lists[i].get_attribute('id')
                sql_query = ("SELECT job_id FROM skills WHERE job_id = %s")
                value = (job_id,)
                db_cursor.execute(sql_query, value)
                query_result = db_cursor.fetchone()
                if query_result:
                    continue
                skill_list = get_skills(job_lists[i])
                if len(skill_list) == 0:
                    continue
                sql_query = "INSERT INTO skills (job_id, skills) VALUES (%s, %s)"
                value = (job_id, json.dumps(skill_list))
                db_cursor.execute(sql_query, value)
                dataBase.commit()
                print(job_id, skill_list)
        except:
            pass
        current_page = current_page + 1

    return True, "Finished"


if __name__ == "__main__":
    driver = create_drive("localhost:" + str(config.port))
    delete_cache(driver)
    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="upwork"
    )
    db_cursor = dataBase.cursor()
    sql_query = "SELECT email_address FROM accounts WHERE NOT country = 'United States' ORDER BY id DESC LIMIT 1"
    db_cursor.execute(sql_query,)
    query_result = db_cursor.fetchone()
    last_created_email = query_result[0]
    state, msg = sign_in_upwork(driver, last_created_email, config.password)
    time.sleep(10)
    print("The scraper has started working...")
    if driver is None:
        driver = create_drive("localhost:" + str(config.port))
    try:
        state, msg = main(driver, dataBase, db_cursor)
    except:
        pass
    dataBase.close()
