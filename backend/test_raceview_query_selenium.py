from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re

driver = webdriver.Chrome()

driver.get("https://il.raceview.net/")

search = driver.find_element(By.TAG_NAME, "input")

search.send_keys("בועז בילגורי")
search.send_keys(Keys.ENTER)

# wait for redirect...

url = driver.current_url

print(url)