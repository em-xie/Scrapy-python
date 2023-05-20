import scrapy

from ArticleSpider.utils import zhihu_login_sel


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit={1}&offset={2}&platform=desktop&sort_by=default"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def start_requests(self):
        # from utils.code import Login
        l = zhihu_login_sel.Login("xxxx","xxxx",6)
        cookies = l.login_baidu()
        # l = Login("用户名", "密码", 6)
        # cookies = l.login()
        print("获取到cookies: ", cookies)
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers, cookies=cookies, dont_filter=True,callback=self.parse)


    def parse(self, response, **kwargs):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        # all_urls = response.css("a::attr(href)").extract()
        # all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        # for url in all_urls:
        #     match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
        #     if match_obj:
        #         #如果提取到question相关的页面则下载后交由提取函数进行提取
        #         request_url = match_obj.group(1)
        #         yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
        #     else:
        #         #如果不是question页面则直接进一步跟踪
        #         yield scrapy.Request(url, headers=self.headers, callback=self.parse)
        pass