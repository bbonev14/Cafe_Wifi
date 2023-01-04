import googlemaps
import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

API_KEY = '####GOOGLE MAPS API KEY####'


def get_map_code(cafe_name, cafe_location):
    map_client = googlemaps.Client(key=API_KEY)
    try:
        response = map_client.geocode(cafe_name + cafe_location)
        return response[0]['place_id']
    except IndexError:
        response = map_client.geocode(cafe_location)
        try:
            return response[0]['place_id']
        # If none work return placeholder maps location
        except IndexError:
            return 'ChIJPXZIogjRrBQRoDgTb_rRcGQ'


def get_map_place_img(place_url):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get(place_url)

    try:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//span[text()="Reject all"]'))).click()
    except selenium.common.exceptions.TimeoutException:
        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button/span'))).click()

    # Selenium solution ------
    # img = WebDriverWait(driver, 100).until(
    #     expected_conditions.presence_of_element_located((By.XPATH, '//img[starts-with(@src, "https://lh5")]')))
    # adress = WebDriverWait(driver, 100).until(
    #     expected_conditions.presence_of_element_located((By.CLASS_NAME, 'Io6YTe'))).text
    # name = WebDriverWait(driver, 100).until(
    #     expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[1]'))).text
    # img = img.get_attribute("src")

    # BS4 solution -----------
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find('h1', {"jsan": "7.DUwDvf,7.fontHeadlineLarge"})
    name = h1.find('span').text

    address = soup.find('div', {'class': 'Io6YTe'}).text

    btn = soup.find('button', {"jsaction": "pane.heroHeaderImage.click"})
    img = btn.find('img')

    location = name + ' ' + address
    return name, img['src'], location
