import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import unquote
import time
import os

# local import
from dotenv import load_dotenv


class Tistory:
    def __init__(self, blogUrl):
        # local params
        load_dotenv()
        self.app_id = os.environ.get("TISTORY_APP_ID")
        self.secret_key = os.environ.get("TISTORY_SECRET_KEY")
        self.tistory_id = os.environ.get('TISTORY_ID')
        self.tistory_pwd = os.environ.get('TISTORY_PWD')
        self.tistory_rss = blogUrl + "rss"

        # Github Actions params
        # self.app_id = os.environ['TISTORY_APP_ID']
        # self.secret_key = os.environ['TISTORY_SECRET_KEY']
        # self.tistory_id = os.environ['TISTORY_ID']
        # self.tistory_pwd = os.environ['TISTORY_PWD']

        # Etc params
        self.callback_url = blogUrl
        self.oauth_url = 'https://www.tistory.com/oauth/authorize'
        self.access_token = None

        # selenium setting params
        self.webdriver_options = webdriver.ChromeOptions()
        self.webdriver_options.add_argument('headless')

    def login_kakao(self, browser):
        """
        login kakao account

        :param browser: chrome webdriver (windows: .exe)
        :return:
        """
        browser.get(self.oauth_url + "?client_id=" + self.app_id
                    + "&redirect_uri=" + self.callback_url + "&response_type=code")
        browser.find_element(By.CLASS_NAME, "txt_login").click()
        time.sleep(5)
        username = browser.find_element(By.ID, "id_email_2")
        password = browser.find_element(By.ID, "id_password_3")
        username.send_keys(self.tistory_id)
        password.send_keys(self.tistory_pwd)
        browser.find_element(By.CLASS_NAME, "btn_confirm").click()
        time.sleep(5)
        browser.get(browser.current_url)

    def confirm_tistory_oauth(self, browser):
        """
        clicking confirm button in tistory oauth page

        :param browser: chrome webdriver (windows: .exe)
        :return:
        """
        time.sleep(5)
        browser.get(browser.current_url)
        try:
            time.sleep(5)
            browser.find_element(By.ID, "contents") \
                .find_element(By.CLASS_NAME, "buttonWrap") \
                .find_element(By.CLASS_NAME, "confirm").click()
            browser.get(browser.current_url)
            time.sleep(5)
            if "code" in browser.current_url:
                url = unquote(unquote(browser.current_url.encode('utf8')))
                end = url.find("state=")
                start = url.find("code=")
                code = url[start + 5:end]
                response = requests.get(
                    "https://www.tistory.com/oauth/access_token?client_id=" + self.app_id
                    + "&client_secret=" + self.secret_key
                    + "&redirect_uri=" + self.callback_url
                    + "&code=" + code
                    + "&grant_type=authorization_code")
                if response.status_code == 200:
                    access_token = response.text.split('=')[1]
                    return access_token
                else:
                    assert "Failed to generate access token: status error"
        finally:
            browser.quit()
        return None

    def get_access_token(self):
        """
        generate access-token automatically

        :return: access-token
        """
        browser = webdriver.Chrome(
            executable_path='./chromedriver/chromedriver.exe',
            options=self.webdriver_options
        )
        self.login_kakao(browser)
        self.access_token = self.confirm_tistory_oauth(browser)
        if self.access_token is None:
            assert "Non-existence access token"
        else:
            assert "Generate access token Successfully"
        return self.access_token


if __name__ == "__main__":
    tistory = Tistory('https://dev-rubykim.tistory.com/')
    print(tistory.get_access_token())
