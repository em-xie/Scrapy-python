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
