http://www.taodudu.cc/news/show-890541.html?action=onClick







```
scrapy genspider jobbole news.cnblogs.com
```

![image-20230516210031106](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230516210031106.png)



```
import scrapy


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["news.cnblogs.com"]
    start_urls = ["http://news.cnblogs.com/"]

    def parse(self, response):
        pass

```

调试 

![image-20230516210005177](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230516210005177.png)

```


from scrapy.cmdline import execute

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])
    # execute(["scrapy", "crawl", "zhihu"])
    # execute(["scrapy", "crawl", "lagou"])
```

# xpath基础语法

![image-20230516211313752](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230516211313752.png)

![image-20230517095529729](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517095529729.png)

![image-20230517095722188](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517095722188.png)

## xpath提取元素

![image-20230517102404507](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517102404507.png)

![image-20230517102422322](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517102422322.png)



![image-20230517102922244](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517102922244.png)



![image-20230517102943712](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517102943712.png)



# css选择器

ppt

![image-20230517105032448](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230517105032448.png)

# 模拟登录

pip install undetected_chromedriver

pip install selenium

```
import scrapy


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["news.cnblogs.com"]
    start_urls = ["http://news.cnblogs.com/"]
    custom_settings = {
        "COOKIES_ENABLED":True
    }

    def start_requests(self):
        import undetected_chromedriver as uc
        browser = uc.Chrome()
        browser.get("https://account.cnblogs.com/signin")
        #     自动化输入，自动化识别滑动验证码并拖动整个自动化过程都会
        input("回车继续：")
        cookies = browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        for url in self.start_urls:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42'
            }
            yield scrapy.Request(url, cookies=cookie_dict, header=headers, dont_filter=True)

    def parse(self, response):
        # url = response.xpath('//*[@id="entry_741926"]/div[2]/h2/a/@href').extract_first("")
        # url = response.xpath('//*[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        url = response.css('div#news_list h2 a::attr(href)').extract()
        pass

```

# 编写spider完成抓取过程

```
    def parse(self, response):
        # url = response.xpath('//*[@id="entry_741926"]/div[2]/h2/a/@href').extract_first("")
        # url = response.xpath('//*[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        # url = response.css('div#news_list h2 a::attr(href)').extract()

        # post_nodes = response.css('#news_list .news_block')
        # for post_node in post_nodes:
        #     image_url = post_node.css('.entry_summary a img::attr(href').extract_first("")
        #     post_url = post_node.css('h2 a::attr(href)').extract_first("")
        #     yield Request(url=parse.urljoin(response.start_urls, post_url), meta={"front_image_url": image_url},
        #                   callback=self.parse_detail)

        # next_url = response.css("div.pager a:last-child::text").extract_first("")
        next_url = response.xpath("//a[contains(text(),'Next >')]/@href").extract_first("")
        yield Request(url=parse.urljoin(response.start_urls, next_url), callback=self.parse)

        # if next_url == "Next >":
        #     next_url = response.css("div.pager a:last-child::attr(href").extract_first("")
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        pass

```

# 提取详情页信息

![image-20230518145843328](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230518145843328.png)



![image-20230518152700078](E:\PyCode\Scrapy-python\Scrapy-note\scrapy安装配置爬取技术文章\image-20230518152700078.png)

```
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


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["news.cnblogs.com"]
    start_urls = ["http://news.cnblogs.com/"]
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

    # @property
    def start_requests(self):
        cookies = []
        self.broswer = uc.Chrome()
        try:
            self.broswer.maximize_window()
        except:
            pass

        url = "https://news.cnblogs.com/"
        self.broswer.get(url)
        # 账号 + 密码 方式(鼠标移动，点击)
        time.sleep(2)
        self.broswer.find_element(By.CSS_SELECTOR, '#login_area > a:nth-child(1)').click()
        time.sleep(2)
        # 在输入账号密码，通过“control+a”覆盖浏览器自动填充的内容
        self.broswer.find_element(By.CSS_SELECTOR, '#mat-input-0').send_keys(Keys.CONTROL + "a")
        # self.broswer.find_element_by_css_selector('#mat-input-0').send_keys(Keys.CONTROL + "a")
        time.sleep(2)
        self.broswer.find_element(By.CSS_SELECTOR, '#mat-input-0').send_keys(self.username)
        # self.broswer.find_element_by_css_selector('#mat-input-0').send_keys(self.username)
        self.broswer.find_element(By.CSS_SELECTOR, '#mat-input-1').send_keys(Keys.CONTROL + "a")
        # self.broswer.find_element_by_css_selector('#mat-input-1').send_keys(Keys.CONTROL + "a")
        time.sleep(2)
        self.broswer.find_element(By.CSS_SELECTOR, '#mat-input-1').send_keys(self.password)
        # self.broswer.find_element_by_css_selector('#mat-input-1').send_keys(self.password)
        # 点击登录
        time.sleep(2)
        self.broswer.find_element(By.CSS_SELECTOR,
                                  'body > app-root > app-sign-in-layout > div > div > app-sign-in > app-content-container > div > div > div > form > div > button').click()
        # self.broswer.find_element_by_css_selector(
        # 'body > app-root > mat-sidenav-container > mat-sidenav-content > div > div > app-sign-in > app-content-container > div > div > form > div > button > span.mat-button-wrapper').click()
        time.sleep(2)
        input("请完成验证码识别后，点击回车：")
        """
        1.通过上述的方式实现登录后，cookies在浏览器中已经有了，要做的就是获取
        2.Selenium提供了get_cookies来获取登录cookies
        4.然后的关键就是保存cookies，之后请求从文件中读取cookies就可以省去每次都要登录一次的
        5.当然可以把cookies返回回去，但是之后的每次请求都要先执行一次login没有发挥cookies的作用
        """
        cookies = self.broswer.get_cookies()

        cookies_dict = {}
        # 在提取cookies时，其实只要其中name和value即可，其他的像domain等可以不用
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        for url in self.start_urls:
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
            }
            yield scrapy.Request(url, headers=headers, cookies=cookies,dont_filter=True,callback=self.parse)

    def parse(self, response, **kwargs):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        post_nodes = response.css('#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            post_url = post_node.css('h2 a::attr(href)').extract_first("")

            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
            break

        # next_url = response.css("div.pager a:last-child::text").extract_first("")
        # next_url = response.xpath("//a[contains(text(),'Next >')]/@href").extract_first("")
        # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

        # if next_url == "Next >":
        #     next_url = response.css("div.pager a:last-child::attr(href").extract_first("")
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

        # 提取下一页并交给scrapy进行下载
        # next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            post_id = match_re.group(1)

            """
            article_item = JobboleArticleItem()
            title = response.css("#news_title a::text").extract_first("")
            # title = response.xpath('//*[@id="news_title"]//a/text()')
            create_data = response.css("#news_info .time::text").extract_first("")
            match_re = re.match(".*?(\d+.*)", create_data)
            if match_re:
                create_date = match_re.group(1)
                # create_date = response.xpath('//*[@id="news_info"]//*[@class="time"]/text()')
            content = response.css("#news_content").extract()[0]
            # content = response.xpath('//*[@id="news_content"]').extract()[0]
            tag_list = response.css(".news_tags a::text").extract()
            # tag_list = response.xpath('//*[@class="news_tags"]//a/text()').extract()
            tags = ",".join(tag_list)
            """

            '''
            同步请求代码，在并发要求不是很高时可以采用
            post_id = match_re.group(1)
            html = requests.get(parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            j_data = json.loads(html.text)
            '''

            """
            article_item["title"] = title
            article_item["create_date"] = create_date
            article_item["content"] = content
            article_item["tags"] = tags
            article_item["url"] = response.url
            # 报错：ValueError:Missing scheme in request url:h
            # 上述报错原因：对于图片下载的字段一定要使用list类型，故[response.meta.get("front_image_url", "")]
            if response.meta.get("front_image_url", ""):
                article_item["front_image_url"] = [response.meta.get("front_image_url", "")]
            else:
                article_item["front_image_url"] = []
            """

            item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
            item_loader.add_css("title", "#news_title a::text")
            item_loader.add_css("create_date", "#news_info .time::text")
            item_loader.add_css("content", "#news_content")
            item_loader.add_css("tags", ".news_tags a::text")
            item_loader.add_value("url", response.url)
            if response.meta.get("front_image_url", []):
                item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))

            # article_item = item_loader.load_item()
            # print(parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          meta={"article_item": item_loader, "url": response.url}, callback=self.parse_nums)

    def parse_nums(self, response):
        j_data = json.loads(response.text)
        item_loader = response.meta.get("article_item", "")

        praise_nums = j_data["DiggCount"]
        fav_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

        item_loader.add_value("praise_nums", j_data["DiggCount"])
        item_loader.add_value("fav_nums", j_data["TotalView"])
        item_loader.add_value("comment_nums", j_data["CommentCount"])
        item_loader.add_value("url_object_id", get_md5(response.meta.get("url", "")))
        '''
        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["url_object_id"] = common.get_md5(article_item["url"])
        '''

        article_item = item_loader.load_item()

        yield article_item

```

```
# -*- coding: utf-8 -*-
__author__ = 'bobby'
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    #从字符串中提取出数字
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

if __name__ == "__main__":
    print (get_md5("http://jobbole.com".encode("utf-8")))
```

```
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst, Identity
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + "-bobby"


def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "0000-00-00"


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


# def gen_suggests(index, info_tuple):
#     #根据字符串生成搜索建议数组
#     used_words = set()
#     suggests = []
#     for text, weight in info_tuple:
#         if text:
#             #调用es的analyze接口分析字符串
#             words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
#             anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
#             new_words = anylyzed_words - used_words
#         else:
#             new_words = set()
#
#         if new_words:
#             suggests.append({"input":list(new_words), "weight":weight})
#
#     return suggests

class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # input_processor = MapCompose(add_author, add_test), # 测试用
        output_processor=Identity()
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(
        output_processor=Join(separator=",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(fav_nums)
        """
        params = (
            self.get("title", ""),
            self.get("url", ""),
            self.get("url_object_id", ""),
            self.get("front_image_path", ""),
            self.get("front_image_url", ""),
            self.get("parise_nums", 0),
            self.get("comment_nums", 0),
            self.get("fav_nums", 0),
            self.get("tags", ""),
            self.get("content", ""),
            self.get("create_date", "0000-00-00"),
        )

        return insert_sql, params

    # def save_to_es(self):
    #     article = ArticleType()
    #     article.title = self['title']
    #     article.create_date = self["create_date"]
    #     article.content = remove_tags(self["content"])
    #     article.front_image_url = self["front_image_url"]
    #     if "front_image_path" in self:
    #         article.front_image_path = self["front_image_path"]
    #     article.praise_nums = self["praise_nums"]
    #     article.fav_nums = self["fav_nums"]
    #     article.comment_nums = self["comment_nums"]
    #     article.url = self["url"]
    #     article.tags = self["tags"]
    #     article.meta.id = self["url_object_id"]
    #
    #     article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10),(article.tags, 7)))
    #
    #     article.save()
    #
    #     redis_cli.incr("jobbole_count")

    # return

```

```
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from datetime import datetime, date
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
# from models.es_types import ArticleType
from w3lib.html import remove_tags

import MySQLdb
import MySQLdb.cursors
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False, default=json_serial) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipleline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item

class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.0.106', 'root', 'root', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"]))
        self.cursor.execute(insert_sql, (item.get("title", ""), item["url"], item["create_date"], item["fav_nums"]))
        self.conn.commit()


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常
        return item

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print (failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
```

```
# Scrapy's settings for ArticleSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
BOT_NAME = "ArticleSpider"

SPIDER_MODULES = ["ArticleSpider.spiders"]
NEWSPIDER_MODULE = "ArticleSpider.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "ArticleSpider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "ArticleSpider.middlewares.ArticlespiderSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "ArticleSpider.middlewares.ArticlespiderDownloaderMiddleware": 543,
#}
DOWNLOADER_MIDDLEWARES = {
    # 'ArticleSpider.middlewares.JSPageMiddleware': 1,
   # 'ArticleSpider.middlewares.RandomUserAgentMiddlware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "ArticleSpider.pipelines.ArticlespiderPipeline": 300,
#}
ITEM_PIPELINES = {
   # 'ArticleSpider.pipelines.JsonExporterPipleline': 2,
   # # 'scrapy.pipelines.images.ImagesPipeline': 1,
   #  'ArticleSpider.pipelines.ArticleImagePipeline': 1,
    'ArticleSpider.pipelines.MysqlTwistedPipline': 1,
    # 'ArticleSpider.pipelines.ElasticsearchPipeline': 1,
    # 'ArticleSpider.pipelines.JsonWithEncodingPipeline': 1
}
IMAGES_URLS_FIELD = "front_image_url"
project_dir = os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE = os.path.join(project_dir, 'images')

import sys
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'ArticleSpider'))

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"

RANDOM_UA_TYPE = "random"
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

MYSQL_HOST = "127.0.0.1"
MYSQL_DBNAME = "article_spider"
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"


SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"

```

