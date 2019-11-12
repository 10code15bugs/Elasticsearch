# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os
from selenium import webdriver
import datetime
import pickle
import time
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
from ArticleSpider.items import LagouJobItemLoader,LagouJobItem
from ArticleSpider.settings import BASE_DIR
#from scrapy.xlib.pydispatch import dispatcher
#from scrapy import signals#信号
class LagouCrawler(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    #redis_key = 'lagou:start_urls'
    start_urls = ['https://www.lagou.com/']
    headers = {
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com/",
        # "USER_AGENT" : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'

    }
    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        #Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r"jobs/\d+.html.*"), callback='parse_job', follow=True),
    )


    '''def __init__(self, **kwargs):
        
        #self.browser=webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe")
        chrome_option =webdriver.ChromeOptions()
        chrome_option.add_argument('--headless')
        
        self.browser = webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe",
                                    chrome_options=chrome_option)
        super(LagouCrawler, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)'''

    '''def spider_closed(self, spider):

     #当爬虫退出的时候关闭chrome
         print ("spider closed")
         self.browser.quit()'''


    def start_requests(self):
        # 去使用selenium模拟登录后拿到cookie交给scrapy的request使用
        # 1、通过selenium模拟登录
        # 从文件中读取cookies
        headers = {
            "HOST": "www.lagou.com",
            "Referer": "https://www.lagou.com/",
            # "USER_AGENT" : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'

        }
        cookies = []
        if os.path.exists(BASE_DIR + "/cookies/lagou.cookie"):
            cookies = pickle.load(open(BASE_DIR + "/cookies/lagou.cookie", "rb"))

        if not cookies:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.keys import Keys
            chrome_option = Options()
            chrome_option.add_argument('--disable-extensions')
            chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
            browser = webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe",
                                    chrome_options=chrome_option)
            #from selenium import webdriver
            #browser = webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe")
            browser.get("https://passport.lagou.com/login/login.html")
            browser.find_element_by_xpath("/html/body/section/div[2]/div[1]/div[2]/form/div[1]/input").send_keys("13643095504")
            browser.find_element_by_xpath('/html/body/section/div[2]/div[1]/div[2]/form/div[2]/input').send_keys("634498@qxp")
            browser.find_element_by_xpath('/html/body/section/div[2]/div[1]/div[2]/form/div[5]/input').click()
            #browser.find_element_by_xpath('/ html / body / section / div[2] / div[1] / div[2] / form / div[5] / input').click()
            import time
            time.sleep(10)
            cookies = browser.get_cookies()
            # 写入cookie到文件中
            pickle.dump(cookies, open(BASE_DIR + "/cookies/lagou.cookie", "wb"))

        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        for url in self.start_urls:


            yield scrapy.Request(url, dont_filter=True,headers=headers, cookies=cookie_dict)


    #def process_results(self, response, results):
     #   return results

    def parse_job(self, response):

        # 解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title",".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/h3/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/h3/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/h3/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/h3/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.datetime.now())

        job_item = item_loader.load_item()
        print(job_item)
        return job_item
