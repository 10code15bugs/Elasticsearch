 #-*- coding: utf-8 -*-
import scrapy

from scrapy import Spider
from selenium import webdriver
import time
import datetime
from mouse import move,click
import pickle
import re
import os
import json
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from ArticleSpider.settings import BASE_DIR

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    #question的第一页answer的请求url
    start_answer_url ="https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"
    headers={
        "HOST":"www.zhihu.com",
        "Referer":"https://www.zhihu.com",
        #"USER_AGENT" : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'

    }
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    
    def start_requests(self):
        cookies = []
        if os.path.exists(BASE_DIR + r"\cookies\zhihu.cookie"):
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

            browser.get("https://www.zhihu.com/signin")
            browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div[1]/div/form/div[1]/div[2]').click()
            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                Keys.CONTROL + "a")
            browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys("13643095504")
            time.sleep(1)
            browser.find_element_by_css_selector(".SignFlow-password input").send_keys(Keys.CONTROL + "a")
            time.sleep(1)
            browser.find_element_by_css_selector(".SignFlow-password input").send_keys("634498qxp@")
            time.sleep(2)
            # browser.find_element_by_css_selector(".Button SignFlow-submitButton.Button--primary Button--blue").click()
            # browser.find_element_by_xpath('//*[@id = "root"]/div/main/div/div/div[1]/div/form/button').click()
            move(678, 511)
            click()
            time.sleep(6)

            login_success = False
            while not login_success:
                try:
                    notify_ele = browser.find_element_by_class_name("Popover PushNotifications AppHeader-notifications")
                    login_success = True
                    return [scrapy.Request(url=self.start_urls[0], dont_filter=True)]
                except:
                    pass

                try:
                    browser.maximize_window()
                except:
                    pass
                try:
                    english_captcha = browser.find_element_by_class_name('Captcha-englishImg')
                except:
                    english_captcha = None
                try:
                    chinese_captcha = browser.find_element_by_class_name('Captcha-chineseImg')
                except:
                    chinese_captcha = None
                if chinese_captcha:
                    ele_postion = chinese_captcha.location
                    x_relative = ele_postion["x"]
                    y_relative = ele_postion["y"]
                    browser_navigation_panel_height = browser.execute_script(
                    'return window.outerHeight - window.innerHeight;'
                )
                    base64_text = chinese_captcha.get_attribute("src")
                    import base64
                    code = base64_text.replace("data:image/jpg;base64,", '').replace("%0A", "")
                    fh = open("yzm_cn.jpeg", "wb")
                    fh.write(base64.b64decode(code))
                    fh.close()

                    from zheye import zheye
                    z = zheye()
                    position = z.Recognize('yzm_cn.jpeg')
                    last_position = []
                    if len(position) == 2:
                        if position[0][1] > position[1][1]:
                            last_position.append([position[1][1], position[1][0]])
                            last_position.append([position[0][1], position[0][0]])
                        else:
                            last_position.append([position[0][1], position[0][0]])
                            last_position.append([position[1][1], position[1][0]])

                        first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                        second_position = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]

                        move(x_relative + first_position[0],
                         y_relative + browser_navigation_panel_height + first_position[1])
                        click()
                        time.sleep(2)
                        move(x_relative + second_position[0],
                         y_relative + browser_navigation_panel_height + second_position[1])
                        click()

                    # for url in self.start_urls:
                    # yield scrapy.Request(url, dont_filter=True, headers=self.headers)
                    else:
                        last_position.append([position[0][1], position[0][0]])
                        first_position = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]

                        move(x_relative + first_position[0],
                         y_relative + browser_navigation_panel_height + first_position[1])
                        click()
                    time.sleep(1)
                    move(663, 569)
                    click()

                if english_captcha:
                    base64_text = english_captcha.get_attribute("src")
                    import base64
                    code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                    fh = open("yzm_en.jpeg", "wb")
                    fh.write(base64.b64decode(code))
                    fh.close()

                    from tools.yundama_requests import YDMHttp
                    yundama = YDMHttp("zzzzqxp", "634498qxp", 8954, "fd03eddd0dc7ebe6eb4ce5c00012bb31")
                    code = yundama.decode("yzm_en.jpeg", 5000, 60)
                    while True:
                        if code == "":
                            code = yundama.decode("yzm_en.jpeg", 5000, 60)
                        else:
                            break
                    browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div[1]/div/form/div[4]/div/div/div[1]/input').send_keys(
                    Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div[1]/div/form/div[4]/div/div/div[1]/input').send_keys(code)


                    time.sleep(1)
                    move(663, 544)
                    click()
                    time.sleep(2)
                time.sleep(1)
                browser.get("https://www.zhihu.com/")

                cookies = browser.get_cookies()
                pickle.dump(cookies,open(r'D:\scrapytest\ArticleSpider\cookies\zhihu.cookie','wb'))
                cookie_dict={}
                for cookie in cookies:
                    cookie_dict[cookie["name"]]=cookie["value"]#cookie储存到本地后就可以在开始打开获取，就不用seleniun
                return [scrapy.Request(url=self.start_urls[0],dont_filter=True,cookies=cookie_dict,headers=self.headers)]

        time.sleep(1)
        browser.get("https://www.zhihu.com/")

        cookies = browser.get_cookies()
        pickle.dump(cookies, open(BASE_DIR + r"\cookies\zhihu.cookie", 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]  # cookie储存到本地后就可以在开始打开获取，就不用seleniun
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict, headers=self.headers)]

    def parse(self,response):
        #print(response.text)
        #提取出html页面中的所有url 并跟踪这些url进行一步爬取
        #如果提取的url中格式为/question/xxx 就下载之后直接进入解析函数
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        #all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            try:
                match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
                if match_obj:
                #如果提取到question相关的页面则下载后交由提取函数进行提取：
                    requese_url = match_obj.group(1)
                    question_id = match_obj.group(2)
                    yield scrapy.Request(requese_url,headers=self.headers,
                                         callback=self.parse_question)
                    #break  # 调试方便
                else:
                #如果不是question页面则直接进一步跟踪
                    #pass
                    yield scrapy.Request(url,headers=self.headers,callback=self.parse)

            except:
                pass


    def parse_question(self, response):
        header={"Referer":response.url}
        # 处理question页面，从页面中提取出具体的queen item
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))
        item_loder =ItemLoader(item=ZhihuQuestionItem(),response=response)
        item_loder.add_css('title',"h1.QuestionHeader-title::text")
        item_loder.add_css('content', ".QuestionHeader-detail")
        item_loder.add_value('url',response.url)
        item_loder.add_value('zhihu_id', question_id)
        item_loder.add_css('answer_num','.List-headerText span::text')
        item_loder.add_css('comments_num', '.QuestionHeader-Comment button::text')
        item_loder.add_css('watch_user_num', '.NumberBoard-itemValue::text')#list 第一个为关注数 第二个浏览数
        item_loder.add_css('click_num', '.NumberBoard-itemValue::text')
        item_loder.add_css('topics','.QuestionHeader-topics .Popover div::text')
        question_item = item_loder.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 5, 0), headers=header,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self,response):
        #处理question的answer
        aheader = {"Referer": response.url}
        ans_json= json.loads(response.text)
        is_end=ans_json['paging']['is_end']
        totals_totals = ans_json['paging']['totals']
        next_url = ans_json['paging']['next']
        #提取answer具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["created_time"] = answer["created_time"]
            answer_item["updated_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            print(answer_item["zhihu_id"],answer_item["url"],answer_item["question_id"],answer_item["author_id"],answer_item["content"],answer_item["praise_num"],answer_item["comments_num"],answer_item["created_time"],answer_item["updated_time"],answer_item["crawl_time"])
            yield answer_item
        if not is_end:
            
            for i in range(1):
                yield scrapy.Request(next_url,headers=aheader,callback=self.parse_answer)
