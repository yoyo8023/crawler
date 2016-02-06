# coding:utf8
import logging
import sys
from datetime import datetime, timedelta

from conf.settings import LOG_DIR
from ifeng_spider import IFengSpider
from sina_spider import SinaSpider
from souhu_spider import SouhuSpider

import logging

logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_DIR + 'test.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


if __name__ == '__main__':
    now_time = datetime.now()
    now_time += timedelta(hours=-10)
    now_time_str = now_time.strftime("%Y-%m-%d %H:%M:%S")
    print now_time_str
    if sys.argv[1] == 'sina':
        logger.info('sina')
        sina = SinaSpider(now_time_str)
        sina.main()
    if sys.argv[1] == 'souhu':
        logger.info('souhu')
        souhu = SouhuSpider(now_time_str)
        souhu.main()
        souhu.pic_main()
    if sys.argv[1] == 'ifeng':
        logger.info('ifeng')
        ifeng = IFengSpider(now_time_str)
        ifeng.main()
        ifeng.pic_main()
