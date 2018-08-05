from selenium import webdriver as wd
from bs4 import BeautifulSoup as bs
import sqlite3 as sql

milk_list = []
def get_milk(url):
    bs(driver.page_source, 'lxml')
    url = url
    title = driver.find_element_by_css_selector('.heading h2').text
    price = driver.find_element_by_css_selector('.price_detail strong').text
    photo = driver.find_element_by_css_selector('.thumbBox img').get_attribute('src')
    seller = driver.find_element_by_css_selector('.seller_nickname').text

    milk_list.append(tuple([title, price, photo, url, seller]))
    return milk_list



main_url = 'http://www.11st.co.kr/browsing/BestSeller.tmall?method=getBestSellerMain&dispCtgrNo=1001345'
driver = wd.Chrome(executable_path='chromedriver.exe')

driver.get(main_url)

html = bs(driver.page_source, "lxml")

links = driver.find_elements_by_css_selector('.pup_title a')

seed_url = []
for link in links:
    link = link.get_attribute('href')
    seed_url.append(link)


for i in range(2): #  len(seed_url)로 바꿀것
    page = driver.get(seed_url[i])
    url = seed_url[i]
    result = get_milk(url)
    driver.implicitly_wait(2)
print(result)

conn = sql.connect('11st.db')
with conn:
    cur = conn.cursor()
    cur.execute('drop table if exists Milk')
    cur.execute("CREATE TABLE Milk(Title TEXT, Price INT, Photo TEXT, URL TEXT, Seller TEXT)")
    cur.executemany("INSERT INTO Milk VALUES (?,?,?,?,?)", milk_list)


