# local import
from dotenv import load_dotenv


class Velog:
    def __init__(self, blogUrl):
        self.url = blogUrl
        self.xml = "https://v2.velog.io/rss/" + self.url[self.url.find("@") + 1:]
        self.contents = []


if __name__ == "__main__":
    velog = Velog("https://velog.io/@rubyhae")

