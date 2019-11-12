#from scrapy import cmdline
#导入cmdline模块,可以实现控制终端命令行。
from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#execute(['scrapy','crawl','cnblogs'])
execute(['scrapy','crawl','zhihu'])
#execute(['scrapy','crawl','lagou'])
#execute(['scrapy','crawl','movie'])
#用exec入运行scrapy的命令。ute（）方法，输/7789