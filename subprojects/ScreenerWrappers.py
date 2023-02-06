import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def yahoo_screener(user: str, password: str, screener_id: str):

    attempts = 0
    symbols = set()

    while attempts < 5:

        try:
            options_ = Options()

            options_.add_argument('--no-sandbox')
            options_.add_argument('--headless')
            options_.add_argument("start-maximized")
            options_.add_argument("disable-infobars")
            options_.add_argument("--disable-extensions")
            options_.add_argument("window-size=1920x1080")
            options_.add_argument('--blink-settings=imagesEnabled=false')
            options_.add_argument("--remote-debugging-port=9222")

            chromedriver_path = '/usr/local/bin/chromedriver'
            chrome_driver = webdriver.Chrome(chromedriver_path, options=options_)
            chrome_driver.delete_all_cookies()

            email = user
            passwd = password

            url = 'https://login.yahoo.com/?.src=finance&.intl=us&.lang=en-US&.done=https%3A%2F%2Ffinance.yahoo.com%2Fscreener%2F&activity=uh-signin&pspid=1183335867'

            chrome_driver.get(url)

            WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-username"]'))).send_keys(
                email)
            WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-signin"]'))).click()
            WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-passwd"]'))).send_keys(
                passwd)
            WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-signin"]'))).click()

            url = 'https://finance.yahoo.com/screener/' + screener_id

            chrome_driver.get(url)

            time.sleep(2)

            html_source = chrome_driver.page_source

            soup = BeautifulSoup(html_source, 'html.parser')

            data = soup.findAll('a', {'class': 'Fw(600) C($linkColor)'})

            for symbol in data:
                symbols.add(symbol.text)

            chrome_driver.quit()

            attempts += 1

            if len(symbols):
                break

        except Exception as e:
            chrome_driver.quit()
            attempts += 1

    return symbols


def finviz_screener():
    '''
    Global options for chromedriver
    '''

    options_ = Options()

    options_.add_argument('--no-sandbox')
    options_.add_argument('--headless')
    options_.add_argument("start-maximized")
    options_.add_argument("disable-infobars")
    options_.add_argument("--disable-extensions")
    options_.add_argument("window-size=1920x1080")
    options_.add_argument('--blink-settings=imagesEnabled=false')
    options_.add_argument("--remote-debugging-port=9222")

    chromedriver_path = '/usr/local/bin/chromedriver'
    chrome_driver = webdriver.Chrome(chromedriver_path, options=options_)
    chrome_driver.delete_all_cookies()

    url = 'https://finviz.com/screener.ashx?v=111&f=geo_usa,sh_avgvol_o300,sh_price_u10,ta_change_u20&ft=4'
    chrome_driver.get(url)

    html_source = chrome_driver.page_source

    soup = BeautifulSoup(html_source, 'html.parser')

    data = soup.findAll('a', {'class': 'screener-link-primary'})
    symbols = set()
    for symbol in data:
        symbols.add(symbol.text)

    chrome_driver.quit()
