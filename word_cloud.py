import json
import re
from collections import Counter
from urllib import request

import matplotlib.pyplot as plt
import wordcloud
from bs4 import BeautifulSoup
from konlpy.tag import Komoran

img = wordcloud.WordCloud(
    font_path="font.ttf", width=1200, height=800, background_color="white",
)

dummy_words = ["기자", "뉴스", "구독"]

kt = Komoran()


def normalize_string(text: str) -> str:
    text = re.sub(r"function .+|//.*\n", "", text)
    text = re.sub(r" *.+\n *.+\n| *\n *| {2,}", "", text)
    text = " ".join(text.split())
    return text


def parse_body(url: str) -> str:
    article_body: str = ""
    for bs in BeautifulSoup(
        request.urlopen(url), "lxml", from_encoding="UTF-8"
    ).find_all("p", {"dmcf-ptype": "general"}):
        article_body += " " + bs.text

    return normalize_string(article_body)


class DaumNews(object):
    def __init__(self):
        self._titles: list = []
        self._links: list = []
        self.site = BeautifulSoup(
            request.urlopen("https://media.daum.net/").read(),
            "lxml",
            from_encoding="UTF-8",
        )

        self._parse_page()

        self._links = list(set(self._links))

    def _parse_page(self):
        for item in self.site.find_all(
            "a", {"href": re.compile(r"https://v.daum.net/v/")}
        ):
            _title = normalize_string(item.text)
            if _title:
                self._titles.append(_title)
            self._links.append(item["href"])

        for item in self.site.find_all("strong", {"class": re.compile(r"tit_\w+")}):
            _title = normalize_string(item.text)
            if _title:
                self._titles.append(_title)

    def get_article_body(self) -> str:
        for link in self._links:
            yield parse_body(link)

    @property
    def titles(self) -> tuple:
        return tuple(set(self._titles))


daum_news = DaumNews()
nouns = []

titles = daum_news.titles

for title in titles:
    for noun in kt.nouns(title):
        if len(noun) > 1 and noun not in dummy_words:
            nouns.append(noun)

for body in daum_news.get_article_body():
    for noun in kt.nouns(body):
        if len(noun) > 1 and noun not in dummy_words:
            nouns.append(noun)

word_count: dict = {}
for k, v in Counter(nouns).most_common(100):
    word_count[k] = v

with open("word_cloud.json", "w", encoding="utf8") as f:
    f.write(json.dumps(word_count, ensure_ascii=False))

img.generate_from_frequencies(word_count)

plt.figure(figsize=(16, 8))
plt.axis("off")
plt.imshow(img)
plt.savefig("word_cloud_result.png")
