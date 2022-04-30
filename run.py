from gitblog import *
from tistory import *
import markdown2
from sys import platform
from dateutil.parser import parse


def personal_setting(head, body):
    """
    personal user setting function

    :param head: title in the post
    :param body: content in the post
    
    return head, body
    """
    def code_line(text):
        """
        preprocess the code blocks

        :param text: content in the post
        
        return the pre-processed content
        """
        text = text.split('\n')
        for idx, b in enumerate(text):
            if "```" in b:
                if "<pre><code>" in b:
                    text[idx] = b[:11]
                else:
                    if len(b) == 3:
                        text[idx] = ""
        return '\n'.join(text)

    return head, code_line(body)


def update_post(githubBlog, tistory):
    """
    update the changed post

    :param githubBlog: Github class object
    :param tistory: Tistory class object
    
    return None
    """
    for t_content in tistory.contents:
        for g_content in githubBlog.contents:
            if t_content["title"] == g_content["title"]:
                if parse(g_content["updated"]) > parse(t_content["published"]):
                    for item in tistory.toc:
                        if item["title"] == t_content["title"]:
                            tistory.editing(
                                g_content["title"],
                                g_content["content"],
                                g_content["category"],
                                g_content["tags"],
                                item["id"])
                            break
                break


def create_post(githubBlog, tistory):
    """
    create the non-existence post

    :param githubBlog: Github class object
    :param tistory: Tistory class object
    
    return None
    """
    flag = 0
    for g_content in githubBlog.contents:
        for t_content in tistory.contents:
            if t_content["title"] == g_content["title"]:
                flag = 1
        if flag:
            flag = 0
            continue
        else:
            path = '/' + '/'.join(g_content["link"].split('/')[6:-1]) + ".md"
            head, body = githubBlog.parsing_md(path)
            body = markdown2.markdown(body)
            head, body = personal_setting(head, body)

            tistory.posting(
                head['title'],
                body,
                head['categories'],
                head['tags'],
            )


if __name__ == "__main__":
    target_os = ''
    if platform == "linux" or platform == "linux2":
        target_os = "linux"
    elif platform == "darwin":
        target_os = "_osx"
    elif platform == "win32":
        target_os = "_win.exe"
    
    githubBlog = GithubBlog("https://ruby-kim.github.io")
    tistory = Tistory('https://dev-rubykim.tistory.com/', target_os)

    tistory.get_access_token()
    githubBlog.parsing_xml()
    tistory.parsing_rss()
    tistory.toc_post()

    create_post(githubBlog, tistory)
