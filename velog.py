from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# local import
from dotenv import load_dotenv


class Velog:
    def __init__(self, blogUrl):
        # local params
        load_dotenv()
        self.velog_id = os.environ.get('VELOG_ID')
        self.velog_pwd = os.environ.get('VELOG_PWD')

        # Github Actions params
        # self.velog_id = os.environ['VELOG_ID']
        # self.velog_pwd = os.environ['VELOG_PWD']

        # Etc params
        self.url = blogUrl
        self.rss = "https://v2.velog.io/rss/" + self.url[self.url.find("@") + 1:]
        self.contents = []
        self.isLogin = False

        # selenium setting params
        self.webdriver_options = webdriver.ChromeOptions()
        # self.webdriver_options.add_argument('headless')
        self.webdriver_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        self.webdriver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.webdriver_options.add_experimental_option('useAutomationExtension', False)
        self.webdriver_options.add_argument('--disable-blink-features=AutomationControlled')
        self.browser = webdriver.Chrome(
            executable_path='./chromedriver/chromedriver.exe',
            options=self.webdriver_options
        )

    def login_github(self):
        self.browser.get("https://velog.io/")
        self.browser.find_element(By.CLASS_NAME, "kMMgG").click()
        time.sleep(5)
        self.browser.find_element(By.CLASS_NAME, "bSWsvS").click()
        time.sleep(5)
        self.browser.find_element(By.NAME, "login").send_keys(self.velog_id)
        self.browser.find_element(By.NAME, "password").send_keys(self.velog_pwd)
        self.browser.find_element(By.NAME, "commit").click()
        time.sleep(5)

    def post_new_article(self, head, body):
        if not self.isLogin:
            self.login_github()
        self.browser.get("https://velog.io/")
        self.browser.find_element(By.CLASS_NAME, "dzAQrW").click()
        self.browser.find_element(By.CLASS_NAME, "mobile-only").click()
        time.sleep(5)
        # head, body

    def close_browser(self, browser):
        browser.quit()



if __name__ == "__main__":
    velog = Velog("https://velog.io/@rubyhae")

