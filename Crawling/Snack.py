from selenium import webdriver as wd
from bs4 import BeautifulSoup as bs
import sqlite3 as sql
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
# driver.implicitly_wait( 10 )


# 됐다 안됐다 지맘대로야
# def getMaxPrice(options):
#     maxPrice = 0
#     for i in range(len(options)):
#         option = options[i].text
#         option = int(re.sub(r'\W', '', option))
#         if maxPrice < option:
#             maxPrice = option
#
#     return maxPrice

snack_list = []
def get_snack(url):
    bs(driver.page_source, 'lxml')
    url = url
    title = driver.find_element_by_css_selector('.heading h2').text
    price = driver.find_element_by_css_selector('.price_detail strong').text
    photo = driver.find_element_by_css_selector('.thumbBox img').get_attribute('src')
    # buying = driver.find_element_by_css_selector('.sd_buying .num').text
    seller = driver.find_element_by_css_selector('.seller_nickname').text

    options = driver.find_elements_by_css_selector('.ui_option_list .prdc_price em')
    # maxPrice = getMaxPrice(options)

    snack_list.append(tuple([title, price, photo, url, seller]))
    return snack_list

main_url = "http://www.11st.co.kr/browsing/BestSeller.tmall?method=getBestSellerMain&dispCtgrNo=1001574"

driver = wd.Chrome(executable_path='chromedriver.exe')

driver.get(main_url)

html = bs(driver.page_source, "lxml")
 
links = driver.find_elements_by_css_selector('.pup_title a')

seed_url = []
for link in links:
    link = link.get_attribute('href')
    seed_url.append(link)


for i in range(len(seed_url)): #  len(seed_url)로 바꿀것
    page = driver.get(seed_url[i])
    url = seed_url[i]
    result = get_snack(url)
    driver.implicitly_wait(2)
print(result)

# while seed_url:
#     n = seed_url.pop(0)
#     page = driver.get(n)
#     result =get_snack(page)
#     driver.implicitly_wait(5)
# print(result)


conn = sql.connect('11st.db')
with conn:
    cur = conn.cursor()
    cur.execute('drop table if exists Snack')
    cur.execute("CREATE TABLE Snack(Title TEXT, Price INT, Photo TEXT, URL TEXT, Seller TEXT)")
    cur.executemany("INSERT INTO Snack VALUES (?,?,?,?,?)", snack_list)
