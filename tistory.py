from itsdangerous import exc
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import unquote
import time
import os
import json
from bs4 import BeautifulSoup

# local import
from dotenv import load_dotenv


class Tistory:
    def __init__(self, blogUrl, platform):
        # local params
        load_dotenv()
        self.app_id = os.environ.get("TISTORY_APP_ID")
        self.secret_key = os.environ.get("TISTORY_SECRET_KEY")
        self.tistory_id = os.environ.get('TISTORY_ID')
        self.tistory_pwd = os.environ.get('TISTORY_PWD')
        self.tistory_rss = blogUrl + "rss"
        self.toc = []
        self.contents = []

        # Github Actions params
        # self.app_id = os.environ['TISTORY_APP_ID']
        # self.secret_key = os.environ['TISTORY_SECRET_KEY']
        # self.tistory_id = os.environ['TISTORY_ID']
        # self.tistory_pwd = os.environ['TISTORY_PWD']
        # self.tistory_rss = blogUrl + "rss"

        # Etc params
        self.callback_url = blogUrl
        self.oauth_url = 'https://www.tistory.com/oauth/authorize'
        self.access_token = None

        # selenium setting params
        self.webdriver_options = webdriver.ChromeOptions()
        self.webdriver_options.add_argument('headless')
        self.chromedriver = "./chromedriver/chromedriver" + platform

    def login_kakao(self, browser):
        """
        login kakao account

        :param browser: chrome webdriver (windows: .exe)
        return None
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
        return None
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

        return access-token
        """
        browser = webdriver.Chrome(
            executable_path=self.chromedriver,
            options=self.webdriver_options
        )
        self.login_kakao(browser)
        self.access_token = self.confirm_tistory_oauth(browser)
        if self.access_token is None:
            assert "Non-existence access token"
        else:
            assert "Generate access token Successfully"

    def posting(self, title, content, category, tag):
        """
        upload the post to tistory

        :param title: title based on github blog setting
        :param content: content based on github blog setting
        :param category: category based on github blog setting
        :param tag: tag based on github blog setting
        return None
        """
        try:
            tistory_url = 'https://www.tistory.com/apis/post/write?'

            headers = {'Content-Type': 'application/json; charset=utf-8'}
            params = {
                'access_token': self.access_token,
                'output': 'json',
                'blogName': 'dev-rubykim',
                'title': title,
                'content': content,
                'visibility': '0',
                'category': str(category[1:-1]),
                'published':'',
                'slogan':'',
                'tag': str(tag[1:-1]),
                'acceptComment': '1',
                'password':''
            }
            data=json.dumps(params)
            response = requests.post(tistory_url, headers=headers, data=data)
            print(response.text)
        except:
            print("Error while uploading post in Tistory!")

    def editing(self, title, content, category, tag, postId):
        """
        update the existence post in tistory

        :param title: title based on github blog setting
        :param content: content based on github blog setting
        :param category: category based on github blog setting
        :param tag: tag based on github blog setting
        :param postId: the target tistory postId

        return None
        """
        try:
            tistory_url = 'https://www.tistory.com/apis/post/modify?'

            headers = {'Content-Type': 'application/json; charset=utf-8'}
            params = {
                'access_token': self.access_token,
                'output': 'json',
                'blogName': 'dev-rubykim',
                'postId': postId,
                'title': title,
                'content': content,
                'visibility': '3',
                'category': str(category[1:-1]),
                'published':'',
                'slogan':'',
                'tag': str(tag[1:-1]),
                'acceptComment': '1',
                'password':''
            }
            data=json.dumps(params)
            response = requests.post(tistory_url, headers=headers, data=data)
            print(response.text)
        except:
            print("Error while editing post in Tistory!")

    def toc_post(self):
        """
        tistory content list
        
        return access-token
        """
        page = 1
        tistory_url = 'https://www.tistory.com/apis/post/list?'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        params = {
            'access_token': self.access_token,
            'output': 'json',
            'blogName': 'dev-rubykim',
        }
        while True:
            params['page'] = page
            data=json.dumps(params)
            response = requests.get(tistory_url, headers=headers, data=data)
            if response.status_code == 400:
                break
            try:
                res = json.loads(response.text)
                for item in res["tistory"]["item"]["posts"]:
                    toc = {
                        "id": item["id"],
                        "postUrl": item["postUrl"],
                        "date": item["date"],
                        "title": item["title"]
                    }
                    self.toc.append(toc)
                page += 1
            except:
                break

    def parsing_rss(self):
        """
        parsing tistory rss
        
        return access-token
        """
        html = requests.get(self.tistory_rss)
        soup = BeautifulSoup(html.text, "html.parser")
        for elem in soup.find_all("item"):
            article = {
                "title": elem.find("title").get_text(),
                "link": elem.find("guid").get_text("ispermalink"),
                "published": elem.find("pubdate").get_text(),
                "category": elem.find("category").get_text(),
                "tags": [c.get_text() for c in elem.find_all("category")],
            }
            self.contents.append(article)
