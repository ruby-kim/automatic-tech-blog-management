import pytz
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os
from github import Github

# local import
from dotenv import load_dotenv


def get_github_repo(access_token, repo_name):
    """
    get github repository info

    :param access_token: Personal Access Token from Github
    :param repo_name: repository name
    :return: repository object
    """
    g = Github(access_token)
    repository = g.get_user().get_repo(repo_name)
    return repository


def get_repo_specific_file_content(repository, file_path):
    """
    get the specific file from github repository

    :param repository: repository object
    :param file_path: file path
    :return: raw content of the decoded target file
    """
    target_file = repository.get_contents("source/_posts" + file_path)
    raw_content = target_file.decoded_content
    return raw_content.decode('utf-8')


def preprocess(content, target_path):
    """
    preprocess the raw content

    :param content: the decoded target file
    :return: content_head(dict), content_body(str)
    """
    def rindex(lst, val):
        lst.reverse()
        i = lst.index(val)
        lst.reverse()
        return len(lst) - i - 1

    # separate head and body part
    content_head_row \
        = content[0:content.rfind("---") + 3].replace("---", "").strip().split("\n")
    content_body_split_start = rindex(content.split("\n"), "---")
    content_body_row = content.split("\n")[content_body_split_start + 1:]

    # head preprocessing
    content_head = {}
    for head in content_head_row:
        colon = head.find(':')
        key = head[:colon]
        value = head[colon + 1:].replace('"', '').replace("\u200d", '').strip()

        if key == 'img':
            value = f"https://github.com/ruby-kim/ruby-kim.github.io/blob/master{value}?raw=true"
        content_head[key] = value

    # body preprocessing
    content_body = []
    target_path_name = '/'.join(target_path.split("/")[1:]).replace(".md", "")
    for body in content_body_row:
        if '![]' in body and '.png)' in body:
            uploaded_date = content_head["date"].split()[0].replace('-', '/')
            img_filename = body.replace("![](", "").replace(")", "")
            body = body.replace(img_filename, f"https://github.com/ruby-kim/ruby-kim.github.io/blob/master/"
                                              f"{uploaded_date + '/' + target_path_name + '/' + img_filename}?raw=true")
        content_body.append(body)
    return content_head, '\n'.join(content_body)


class GithubBlog:
    def __init__(self, blogUrl):
        self.url = blogUrl
        self.xml = blogUrl + "/atom.xml"
        self.contents = []
        self.curTime = datetime.now(pytz.utc).isoformat()
        self.md_head = {}
        self.md_body = ""

    def parsing_md(self, target_path):
        # local params
        load_dotenv()
        repo = get_github_repo(os.environ.get('MY_GITHUB_BLOG_BACKUP'), 'koBlog_backup')

        # # Github action params
        # repo = get_github_repo(os.environ['MY_GITHUB_BLOG_BACKUP'], 'koBlog_backup')

        file = get_repo_specific_file_content(repo, target_path)
        self.md_head, self.md_body = preprocess(file, target_path)
        return self.md_head, self.md_body

    def parsing_xml(self):
        html = requests.get(self.xml)
        soup = BeautifulSoup(html.text, "html.parser")
        for elem in soup.find_all("entry"):
            article = {
                "title": elem.find("title").get_text(),
                "link": elem.find("link").get("href"),
                "published": elem.find("published").get_text("published"),
                "updated": elem.find("updated").get_text("updated"),
                "category": elem.find("category").get("term").replace("\u200d", ""),
                "tags": [c.get("term")
                         for idx, c in enumerate(elem.find_all("category")) if idx != 0],
            }
            self.contents.append(article)


# if __name__ == "__main__":
#     githubBlog = GithubBlog("https://ruby-kim.github.io")
#     githubBlog.parsing_xml()
#     githubBlog.parsing_md("/AWS/IAM.md")
