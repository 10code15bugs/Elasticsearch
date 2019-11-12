# -*- coding: utf-8 -*-
import scrapy
import re
import os
import pickle
import time
import json
import datetime
from ArticleSpider.settings import BASE_DIR
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import ArticleSpiderItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader
#from scrapy.xlib.pydispatch import dispatcher
#from scrapy import signals#信号
from selenium import webdriver

class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['cnblogs.com']
    start_urls = []
    for x in range(1):

        urls='https://www.cnblogs.com/sitehome/p/'+str(x+1)
        start_urls.append(urls)
    print(start_urls)
    headers = {
       # "accept-encoding":"gzip, deflate, br",
       # "accept-language":"zh-CN,zh;q=0.9",
        "origin": "https://www.cnblogs.com",
        #"content-type":"application/json; charset=UTF-8",
        "Referer": "https://www.cnblogs.com/",
        "USER_AGENT" :'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
   }

    '''def start_requests(self):
    cookies = []
    if os.path.exists(BASE_DIR + "/cookies/cnblogs.cookie"):
        cookies = pickle.load(open(BASE_DIR + "/cookies/cnblogs.cookie", "rb"))
    # 手动启动chromdriver 有一些js变量。启动chrome之前确保所有的chrome实例已经关闭
    if not cookies:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        browser = webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe")
        browser.get("https://account.cnblogs.com/signin")

        browser.find_element_by_xpath('//*[@id="LoginName"]').send_keys(Keys.CONTROL + "a")
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="LoginName"]').send_keys('634498859@qq.com')
        browser.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.CONTROL + "a")
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="Password"]').send_keys('634498@qxp')
        time.sleep(1)
        browser.find_element_by_xpath('//*[@id="submitBtn"]').click()

        time.sleep(5)
        browser.get("https://www.cnblogs.com")
        cookies = browser.get_cookies()
        pickle.dump(cookies, open(r'D:\scrapytest\ArticleSpider\cookies\cnblogs.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie["name"]] = cookie["value"]
    
    #temp = json.dumps(formdata)
    for url in self.start_urls:
        yield scrapy.Request(url, dont_filter=True,headers=self.headers, cookies=cookie_dict)'''
    '''def __init__(self):

    self.browser=webdriver.Chrome(executable_path=r"D:\scrapytest\ArticleSpider\venv\Scripts\chromedriver.exe")
    super(CnblogsSpider, self).__init__()
    dispatcher.connect(self.spider_closed, signals.spider_closed)

def spider_closed(self, spider):
     #当爬虫退出的时候关闭chrome
    print ("spider closed")
    self.browser.quit()'''


    def parse(self, response):
        #解析列表页中的所有文章url
        time.sleep(2)
        post_nodes=response.css('.post_item_body')
        headers = {

            "Referer": response.url
        }
        for post_node in post_nodes:
            image_url=post_node.css('.post_item_summary img::attr(src)').extract_first()
            post_url=post_node.css('h3 a::attr(href)').extract_first()
            print(post_url)
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url}, callback=self.parse_job)
            #dont_filter=True解除重定向

        #next_url = response.css('#main .pager a::attr(href)').extract()[12]
        #if next_url:


            #yield Request(url= parse.urljoin(response.url, next_url),headers=headers,callback=self.parse)



        #提取文章的具体字段
        '''title=response.xpath('//*[@id="cb_post_title_url"]/text()').extract()[0]#主题
        date=response.xpath('//*[@id="post-date"]/text()').extract()[0]#日期
        match_re=re.match(r'.*?((\d+).(\d+).(\d+))',date)
        if match_re:
            date=match_re.group(1)
        #re3=response.xpath('//*[@id="post_view_count"]/text()').extract()[0]#
        content=response.xpath('// *[ @ id = "cnblogs_post_body"]').extract()'''
        #css
    def parse_job(self, response):
        '''item=ArticleSpiderItem()
        time.sleep(1)
        front_image_url = response.meta.get("front_image_url", "")#文章封面图
        title=response.css('#cb_post_title_url::text').extract()[0]
        date=response.css('#post-date::text').extract()[0]
        match_re=re.match(r'.*?((\d+).(\d+).(\d+))',date)
        if match_re:
            date=match_re.group(1)

        content=response.css('#cnblogs_post_body').extract()

        item['url_object_id'] = get_md5(response.url)
        item['title']=title
        try:
            date=datetime.datetime.strptime(date,"%Y/%m/%d").date()
        except Exception as e:
            date=datetime.datetime.now().date()
        item['date'] = date
        item['url'] = response.url
        item['front_image_url'] = [front_image_url]
        item['content'] = content'''
        #通过itemloader加载item
        #global front_image_url
        front_image_url = response.meta.get("front_image_url", "")
        item_loader= ArticleItemLoader(item=ArticleSpiderItem(),response=response)
        item_loader.add_css('title','#cb_post_title_url::text')
        item_loader.add_value('url',response.url)#直接添加值用add_value()
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_css('date','#post-date::text')
        item_loader.add_value('front_image_url',[front_image_url])
        item_loader.add_css('content','#cnblogs_post_body')

        item=item_loader.load_item()#调用   问题1：会把所以值变成list 2还要加处理函数
        #print(item)
        #item_loader.add_xpath()
        #item_loader.add_value()
        yield item
