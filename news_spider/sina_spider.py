# coding:utf8
import os
import re
import requests
from bs4 import BeautifulSoup

from lib.char_change import sina_change_char
from lib.date_transform import string_transform_timestamp
from lib.mysql_api import insert_news_to_mysql
from lib.oss_api import upload_img_to_oss2
from lib.parser_html import strip_tags

import logging
import logging.config

from lib.source_html import get_tag_html

logging.config.fileConfig(os.path.join('conf', "logging.conf"))
logger = logging.getLogger("example01")


class SinaSpider(object):
    """
    新浪数据抓取
    :param url: 抓取数据的url
    :param start_time: 开始时间
    :param end_time: 结束时间
    """

    def __init__(self, start_time, end_time):
        self.start_timestamp = string_transform_timestamp(start_time)
        self.end_timestamp = string_transform_timestamp(end_time)
        self.flag = 0
        self.article_data_list = list()
        self.url_list = [
            'http://feed.mix.sina.com.cn/api/roll/get?pageid=107&lid=1244&num=30'
            '&versionNumber=1.2.8&page={page}&encode=utf-8&callback=feedCardJsonpCallback',
            'http://feed.mix.sina.com.cn/api/roll/get?pageid=51&lid=740'
            '&num=30&versionNumber=1.2.8&page={page}&encode=utf-8&callback=feedCardJsonpCallback',
        ]
        self.pic_url_list = [
            'http://pic.yule.sohu.com/cate-911401.shtml'
        ]

    def sina(self, url):
        """
        新浪微博数据抓取
        :param url: 抓取数据的url
        """
        content = requests.get(url, timeout=3).text
        content = content.replace('try{feedCardJsonpCallback(', '')
        content = content.replace(');}catch(e){};', '')
        content_dict = eval(content)
        data_list = content_dict['result']['data']
        for data in data_list:
            tmp_dict = dict()
            url = data['url'].replace('\\', '')
            ctime = float(data['ctime'])
            if ctime < self.start_timestamp:
                self.flag = 1
                break
            tmp_dict['ctime'] = ctime
            tmp_dict['source'] = url
            try:
                data_content = requests.get(url, timeout=3).text
            except Exception, info:
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            soup = BeautifulSoup(data_content)
            title = get_tag_html(soup, '#main_title')
            tmp_dict['title'] = title.replace('\\', '')
            digest = get_tag_html(soup, '.ellipsis')
            tmp_dict['digest'] = digest
            # 获取文章内容
            artile = ''
            for a in soup.select("[class~=content] p"):
                for string in a.strings:
                    artile += '<p>'+string.strip()+'</p>'
            tmp_dict['artile'] = artile
            img_list = list()
            # 获取图片内容
            for img in soup.select("[class~=content] img"):
                img_title = img['alt']
                img_url = img['src']
                # 上传图片到阿里云
                status, msg, img_url = upload_img_to_oss2(img_url)
                if status:
                    img_list.append([img_title, img_url])
            tmp_dict['img_list'] = img_list
            tmp_dict['pic_mode'] = 0
            self.article_data_list.append(tmp_dict)

    def main(self):
        for url in self.url_list:
            page = 1
            print url
            while self.flag != 1:
                try:
                    self.sina(url.format(page=page))
                except Exception, info:
                    logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                page += 1
            self.flag = 0
        data = sina_change_char(self.article_data_list)
        insert_news_to_mysql(data)


if __name__ == '__main__':
    s = SinaSpider('2016-1-27 00:00:00', '2016-1-26 23:59:59')
    s.main()
