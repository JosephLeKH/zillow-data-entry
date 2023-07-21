"""
Purpose: This program takes a filtered Zillow link and compile a list of the addresses, prices, and links of the first
41 listings into a Google Sheet using Google Form.
Tools: BeautifulSoup, Selenium
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import json
import os

# URL of the Zillow search
ZILLOW_URL = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22users" \
             "SearchTerm%22%3Anull%2C%22mapBounds%22%3A%7B%22west%22%3A-122.56276167822266%2C%22east%22%3A-122.303896" \
             "32177734%2C%22south%22%3A37.69261345230467%2C%22north%22%3A37.857877098316834%7D%2C%22isMapVisible%22%3" \
             "Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afals" \
             "e%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B" \
             "%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D" \
             "%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%" \
             "22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isList" \
             "Visible%22%3Atrue%2C%22mapZoom%22%3A12%7D"

# Make the soup object
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}
response = requests.get(url=ZILLOW_URL, headers=header).text
soup = BeautifulSoup(response, "lxml")

# Crawl the soup and prepare the data
test = soup.find_all("script", attrs={"type": "application/json"})
rent_data = test[1].text
rent_data = rent_data.replace("<!--", "")
rent_data = rent_data.replace("-->", "")
rent_data = json.loads(rent_data)
rent_data = rent_data["props"]["pageProps"]["searchPageState"]["cat1"]["searchResults"]["listResults"]

# Make the list of links
links_list = []
for i in rent_data:
    link = i["detailUrl"]
    if link[:5] != "https":
        link = "https://www.zillow.com" + link
    links_list.append(link)

# Make the list of prices
prices_list = []
for i in rent_data:
    try:
        price = i["units"][0]["price"]
        prices_list.append(price)
    except KeyError:
        price = i["price"]
        prices_list.append(price)
new_prices_list = [x[:6] for x in prices_list]

# Make the list of addresses
addresses_list = []
for i in rent_data:
    addresses_list.append(i["address"])

# Prepare the Selenium Driver and go to the Form
chrome_driver = os.environ["DRIVER_PATH"]
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
ser = Service(executable_path=chrome_driver, log_path="NUL")
driver = webdriver.Chrome(service=ser, options=options)
driver.get(os.environ["FORM_URL"])

# Fill in the 3 fields for the form for all the 41 listings
for i in range(len(links_list)):
    address_field = driver.find_element(by=By.XPATH,
                                        value="/html/body/div/div[2]/form/div[2]/div/div[2]/div[1]/div/div/div[2]/"
                                              "div/div[1]/div/div[1]/input")
    address_field.click()
    address_field.send_keys(addresses_list[i])

    price_field = driver.find_element(by=By.XPATH,
                                      value="/html/body/div/div[2]/form/div[2]/div/div[2]/div[2]/div/div/div[2]/div/"
                                            "div[1]/div/div[1]/input")
    price_field.click()
    price_field.send_keys(new_prices_list[i])

    link_field = driver.find_element(by=By.XPATH,
                                     value="/html/body/div/div[2]/form/div[2]/div/div[2]/div[3]/div/div/div[2]/div/"
                                           "div[1]/div/div[1]/input")
    link_field.click()
    link_field.send_keys(links_list[i])
    driver.find_element(by=By.XPATH,
                        value="/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span").click()
    driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div[1]/div/div[4]/a").click()

driver.quit()
