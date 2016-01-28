# coding:utf8
import sys

from ifeng_spider import IFengSpider
from sina_spider import SinaSpider
from souhu_spider import SouhuSpider

if __name__ == '__main__':
    if sys.argv[1] == 'sina':
        sina = SinaSpider('2016-1-27 00:00:00')
        sina.main()
    if sys.argv[1] == 'souhu':
        souhu = SouhuSpider('2016-1-26 12:30:00')
        souhu.main()
        souhu.pic_main()
    if sys.argv[1] == 'ifeng':
        ifeng = IFengSpider('2016-1-20 00:00:00')
        ifeng.main()
        ifeng.pic_main()
