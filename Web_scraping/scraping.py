from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import time

DRIVER_PATH = '/Downloads/chromedriver_linux64/chromedriver'
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")



small_alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
diseases=[]
f = open('data.csv', 'a')
for c in small_alpha:
    URL = 'https://www.nhp.gov.in/disease-a-z/'+c
    time.sleep(1)
    driver = webdriver.Chrome(options=options,executable_path=DRIVER_PATH)
    driver.get(URL)
    all_diseases = driver.find_element(By.CLASS_NAME, 'all-disease')
    text = all_diseases.text
    f.write(text)
    diseases.append(text)

f.close()
for a in diseases:
    print(a)


driver.quit()