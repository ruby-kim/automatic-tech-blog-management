import pytz
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os

# local import
from dotenv import load_dotenv


class NaverBlog:
    def __init__(self, blogUrl):
        self.url = blogUrl
        self.xml = blogUrl.replace("https://", "https://rss.") + ".xml"
        self.contents = []
        self.curTime = None

    def parsing_xml(self):
        return


if __name__ == "__main__":
    naverBlog = NaverBlog("https://blog.naver.com/dev_rubykim")


