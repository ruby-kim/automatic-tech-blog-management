from gitblog import *
from tistory import *
from markdown2 import Markdown
from sys import platform


def personal_setting(head, body):
    if "{% post_link 'AWS/intro' %}" in body:
        body = body[:body.index("{% post_link 'AWS/intro' %}")] + "<p>https://ruby-kim.github.io/2022/03/15/AWS/intro/</p>"
    return head, body


if __name__ == "__main__":
    target_os = ''
    if platform == "linux" or platform == "linux2":
        target_os = "linux"
    elif platform == "darwin":
        target_os = "_osx"
    elif platform == "win32":
        target_os = "_win.exe"
    
    markdowner = Markdown()
    githubBlog = GithubBlog("https://ruby-kim.github.io")
    tistory = Tistory('https://dev-rubykim.tistory.com/', target_os)

    head, body = githubBlog.parsing_md("/AWS/EC2.md")
    head, body = personal_setting(head, body)

    tistory.get_access_token()
    tistory.posting(head['title'], markdowner.convert(body), head['categories'], head['tags'])