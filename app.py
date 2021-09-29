import json
import os
import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


class Thread:
    title = ''
    tid = 0
    url = ''

    def __init__(self, tid, title):
        self.tid = tid
        self.title = title


def get_tread_list():
    FORUM_URL = os.getenv('FORUM_URL')
    headers = {
        "User-Agent": ua.random}

    r = requests.get(FORUM_URL, headers=headers);

    soup = BeautifulSoup(r.text, "html.parser")

    print(soup.prettify())

    for top in soup.find_all('tr', class_=re.compile('^top')):
        top.decompose()

    thread_list_soup = soup.find_all('tr', class_="thread");

    thread_list = []

    for thread in thread_list_soup:
        msg = thread.select('tr > td > div > a')[1]
        thread = Thread(int(msg['href'][7:-4]), msg.string)
        thread_list.append(thread)

    return thread_list


def get_new_thread_list(thread_list):
    new_thread_list = []
    last_thread_tid = int(open('last.txt').read())

    for thread in thread_list:
        if thread.tid > last_thread_tid:
            thread.url = 'https://bbs.pediy.com/thread-' + str(thread.tid) + '.htm'
            new_thread_list.append(thread)
        else:
            break
    return new_thread_list


def post2cubox(thread):
    API_URL = os.getenv('CUBOX_API')
    headers = {
        "User-Agent": ua.random,
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        'type': 'url',
        'content': thread.url,
        'title': thread.title,
        'description': '',
        'folder': '看雪备份'
    }

    data = json.dumps(data)
    r = requests.post(API_URL, headers=headers, data=data)
    print(r.text)


if __name__ == '__main__':
    all_thread_list = get_tread_list()
    new_thread_list = get_new_thread_list(all_thread_list)
    if len(new_thread_list) > 0:
        open('last.txt', 'w').write(str(new_thread_list[0].tid))
        for thread in new_thread_list:
            post2cubox(thread)
