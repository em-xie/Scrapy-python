import re
from urllib import parse
import undetected_chromedriver as uc
import scrapy
from scrapy import Request
import requests
import json
from pydispatch import dispatcher
from scrapy import signals
import time
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.common.keys import Keys
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader

from ArticleSpider.utils.common import get_md5

class VideoSpider(scrapy.Spider):
    name = "video"
    start_urls = [
        "https://twitter.com/"
    ]
    handle_httpstatus_list = [404]
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
        self.username = "xxxxxx"
        self.password = "xxxxxx"

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

    def start_requests(self):
        # from utils.code import Login
        # l = Login("用户名", "密码", 6)
        # cookies = l.login()
        # print("获取到cookies: ", cookies)
        # for url in self.start_urls:
        #     yield scrapy.Request(url, headers=self.headers, cookies=cookies, callback=self.parse)

        pass

    def parse(self, response):
        for video in response.css("div.video"):
            yield {
                "name": video.css("h3::text").get(),
                "url": video.css("a::attr(href)").get(),
                "image": video.css("img::attr(src)").get()
            }

        next_page = response.css("a.next-page::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def download_video(self, response):
        name = response.css("h3::text").get()
        video_url = response.css("video source::attr(src)").get()
        yield scrapy.Request(video_url, callback=self.save_video, meta={"name": name})

    def save_video(self, response):
        name = response.meta["name"]
        with open(f"{name}.mp4", "wb") as f:
            f.write(response.body)