# coding:utf8
import sys

path_list = ['/home/prod/deploys/crawler/news_spider',
             '/home/prod/deploys/crawler/news_spider/conf',
             '/home/prod/deploys/crawler/news_spider/lib',
             ]

for path in path_list:
    sys.path.append(path)

from datetime import datetime, timedelta
from ifeng_spider import IFengSpider
from sina_spider import SinaSpider
from souhu_spider import SouhuSpider


if __name__ == '__main__':
    now_time = datetime.now()
    now_time += timedelta(hours=-2)
    now_time_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
    print now_time_str
    if sys.argv[1] == 'sina':
        sina = SinaSpider(now_time_str)
        sina.main()
    if sys.argv[1] == 'souhu':
        souhu = SouhuSpider(now_time_str)
        souhu.main()
        souhu.pic_main()
    if sys.argv[1] == 'ifeng':
        ifeng = IFengSpider(now_time_str)
        ifeng.main()
        ifeng.pic_main()
