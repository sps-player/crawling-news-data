import json
import re
import time
from collections import Counter
from urllib import request

import bs4.element
from bs4 import BeautifulSoup
from konlpy.tag import Komoran
from selenium import webdriver

driver = webdriver.Chrome()
title_list: list = []
article_addresses: list = []
kt = Komoran()


def normalize_string(text: str) -> str:
    text = re.sub(r"function .+|//.*\n", "", text)
    text = re.sub(r" *.+\n *.+\n| *\n *| {2,}", "", text)
    text = " ".join(text.split())
    return text


def get_article_info(url: str) -> list:
    article_body: str = ""
    driver.get(url)
    time.sleep(1.5)
    html = driver.page_source
    _category = None
    bs = BeautifulSoup(html, "lxml")

    for page in bs.find_all("p", {"dmcf-ptype": "general"}):
        article_body += " " + page.text

    for li in bs.find_all("li"):
        li: bs4.element.Tag

        c = li.get("class")
        if not c or len(c) < 2:
            continue
        if c[-1] == "on":
            _category = c[0]

    return [_category, normalize_string(article_body)]


news = BeautifulSoup(request.urlopen("https://media.daum.net/").read(), "lxml",)

for item in news.find_all("a", {"href": re.compile(r"https://v.daum.net/v/")}):
    _title = normalize_string(item.text)
    if _title:
        title_list.append(_title)
    article_addresses.append(item["href"])

for item in news.find_all("strong", {"class": re.compile(r"tit_\w+")}):
    _title = normalize_string(item.text)
    if _title:
        title_list.append(_title)

word_by_category = {
    "society": {},
    "politics": {},
    "economic": {},
    "foreign": {},
    "culture": {},
    "digital": {},
}

for article_url in article_addresses:
    info = get_article_info(article_url)
    category = info[0]
    body = info[1]

    nouns = []

    for noun in kt.nouns(body):
        if len(noun) > 1:
            nouns.append(noun)

    word_count: dict = {}
    for k, v in Counter(nouns).most_common(100):
        word_count[k] = v

    counted = word_by_category[category]
    for word in word_count:
        if word in counted:
            counted[word] += word_count[word]
        else:
            counted[word] = word_count[word]

with open("words_by_category.json", "w", encoding="utf8") as f:
    f.write(json.dumps(word_by_category, ensure_ascii=False))

driver.close()
