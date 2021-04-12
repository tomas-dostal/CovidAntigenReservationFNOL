import time

import selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import re

################################################## fill me ############################################################
# Looking for a reservation on YYYY-MM-DD (you can add multiple dates, ordered by priority. First = the best for you.
# Future improvements: Switch to the other month. Currently searches only on default-displayed month
searching_for = ["2021-04-14", "2021-03-13", "2021-03-11"]

# Information used for a registration form
firstName = "Name"
lastName = "Surname"
phone = "123123123"
# enter a valid email even for testing purposes to be be able to cancel the reservation created !!!
mail = "email@test.com"
#######################################################################################################################


def getReservation():
    try:
        driver.get("https://rezervacecovid.fnol.cz/Pages/Calendar2.aspx?calendarType=Public")
    except WebDriverException:
        print("Request timeout or whatever. Retrying in a few seconds")
        time.sleep(30)

    days = driver.find_elements_by_class_name("order-day")
    full = driver.find_elements_by_class_name("full")

    results = [item for item in days if item not in full]

    if len(results) < 1:
        print("No available slots found")
        return False

    for day in results:
        day_str = re.findall(r"\d+-\d+-\d+", day.get_attribute("outerHTML"))
        matching_results = [date for date in searching_for if date in day_str]

        if len(matching_results) < 1:
            print("On {} there are {} slot(s) available, but I am searching only for {}".format(
                day_str,
                re.findall(r"\d+", day.text.split("\n")[1]),
                searching_for)
            )
        elif len(matching_results) > 0:
            day.click()

            driver.find_element_by_id("firstname").send_keys(firstName)
            driver.find_element_by_id("lastname").send_keys(lastName)
            driver.find_element_by_id("phone").send_keys(phone)
            driver.find_element_by_id("mail").send_keys(Keys.BACKSPACE)  # delete initial @
            driver.find_element_by_id("mail").send_keys(mail)

            term = driver.find_element_by_id("term")
            term.click()

            # selects the first available time slot. Future improvements: user might want to specify preferred time.
            selectBox = driver.find_element_by_class_name("autocomplete")
            selectBox.send_keys(Keys.DOWN)
            selectBox.send_keys(Keys.ENTER)

            driver.find_element_by_class_name("btnConfirm").click()

            try:
                driver.find_element_by_class_name("invalid-label")
                print("Invalid input detected: {}".format(driver.find_element_by_class_name("invalid-label").text))
                driver.close()
                print("Exitting, please correct entered information")
                exit(1)
            except selenium.common.exceptions.NoSuchElementException:
                pass

            print(driver.find_element_by_class_name("notification-body").text)
            driver.close()
            print("Success. You should get an email with time & date and details from FNO.")
            return True


driver = webdriver.Firefox()
while not getReservation():
    time.sleep(10)
