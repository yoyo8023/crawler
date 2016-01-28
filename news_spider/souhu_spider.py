# coding:utf8
import os
import traceback
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from lib.char_change import souhu_change_char
from lib.date_transform import string_transform_timestamp
from lib.mysql_api import insert_news_to_mysql
from lib.oss_api import upload_img_to_oss2
from lib.source_html import get_tag_html

import logging
import logging.config
print os.path.join('conf', "logging.conf")
logging.config.fileConfig(os.path.join('conf', "logging.conf"))
logger = logging.getLogger("example01")


class SouhuSpider(object):
    """
    搜狐微博数据抓取
    :param url: 抓取数据的url
    :param start_time: 开始时间
    :param end_time: 结束时间
    """

    def __init__(self, start_time):
        self.start_timestamp = string_transform_timestamp(start_time)
        self.flag = 0
        self.article_data_list = list()
        self.url_list = [
            'http://yule.sohu.com/tv{page}.shtml',
            'http://yule.sohu.com/movie{page}.shtml',
            'http://music.yule.sohu.com/news{page}.shtml',
        ]
        self.pic_url_list = [
            'http://pic.yule.sohu.com/cate-911401.shtml'
        ]

    def detail_spider(self, url):
        content = requests.get(url, timeout=3).text
        soup = BeautifulSoup(content)
        news_detail_list = list()
        now_year = str(datetime.now().year)
        for data in soup.select("[class~=f14list] li"):
            if data.span:
                date_time = now_year + '-' + data.span.string[2:-1].replace('/', '-') + ':00'
                date_timestamp = string_transform_timestamp(date_time)
                if date_timestamp < self.start_timestamp:
                    self.flag = 1
                    break
                news_detail_list.append(data.a['href'])
        for news in news_detail_list:
            tmp_dict = dict()
            try:
                r = requests.get(news, timeout=3)
            except Exception, info:
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            news_body = r.text
            news_soup = BeautifulSoup(news_body)
            if 'pic' not in news:
                print news
                title = get_tag_html(news_soup, 'h1')
                tmp_dict['title'] = title
                # 获取文章内容
                artile = ''
                for a in news_soup.select("#contentText p"):
                    for string in a.strings:
                        if '_tvId' not in string:
                            artile += '<p>' + string.strip() + '</p>'
                tmp_dict['artile'] = artile
                # 获取图片
                img_list = list()
                for img in news_soup.select("#contentText img"):
                    img_title = img['alt']
                    img_url = img['src']
                    # 上传图片到阿里云
                    status, msg, img_url = upload_img_to_oss2(img_url)
                    if status:
                        img_list.append((img_title, img_url))
                tmp_dict['img_list'] = img_list
                tmp_dict['pic_mode'] = 0
            else:
                title = get_tag_html(news_soup, '[class~=ttl]')
                tmp_dict['title'] = title
                # 获取文章内容
                tmp_dict['artile'] = get_tag_html(news_soup, '[class~=explain]')
                # 获取图片
                img_list = list()
                for img in news_soup.select("#picPlayerTab img"):
                    img_title = img.get('alt') if img.get('alt') else ''
                    img_url = img['src'].replace('st', '')
                    # 上传图片到阿里云
                    status, msg, img_url = upload_img_to_oss2(img_url)
                    if status:
                        img_list.append((img_title, img_url))
                tmp_dict['img_list'] = img_list
                tmp_dict['pic_mode'] = 1
            tmp_dict['source'] = news
            self.article_data_list.append(tmp_dict)

    def main(self):
        for url in self.url_list:
            new_url = url.format(page='')
            try:
                content = requests.get(new_url, timeout=3).text
            except Exception, info:
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            # 获取max page
            content_list = content.split('\n')
            max_page = 0
            for c in content_list:
                if 'var maxPage = ' in c:
                    start_index = c.find('=') + 1
                    max_page = int(c[start_index: -1].strip()) - 1
                    break
            self.detail_spider(url)
            while self.flag != 1 and max_page != 0:
                max_page_str = '_' + str(max_page)
                print url.format(page=max_page_str)
                try:
                    self.detail_spider(url.format(page=max_page_str))
                except Exception, info:
                    logger.debug("Error '%s'" % info)
                    traceback.print_exc()
                max_page -= 1
            self.flag = 0
        data = souhu_change_char(self.article_data_list)
        insert_news_to_mysql(data)

    def pic_main(self):
        for url in self.pic_url_list:
            try:
                content = requests.get(url, timeout=3).text
            except Exception, info:
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            soup = BeautifulSoup(content)
            for data in soup.select("#item-list a"):
                tmp_dict = dict()
                news_url = data['href']
                try:
                    news_body = requests.get(news_url, timeout=3).text
                except Exception, info:
                    logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                    continue
                news_soup = BeautifulSoup(news_body)
                title = get_tag_html(news_soup, '#contentE h2')
                pub_time = get_tag_html(news_soup, '[class~=timt]')
                pub_time = pub_time.replace(u'日期：', '').strip()
                pub_timmestamp = string_transform_timestamp(pub_time + ' 00:00:00')
                if pub_timmestamp < self.start_timestamp:
                    self.flag = 1
                    break
                tmp_dict['title'] = title
                # 获取文章内容
                tmp_dict['artile'] = get_tag_html(news_soup, '[class~=explain]')
                # 获取图片
                img_list = list()
                for img in news_soup.select("#picPlayerTab img"):
                    img_title = img['alt']
                    img_url = img['src'].replace('st', '')
                    # 上传图片到阿里云
                    status, msg, img_url = upload_img_to_oss2(img_url)
                    if status:
                        img_list.append((img_title, img_url))
                tmp_dict['img_list'] = img_list
                tmp_dict['source'] = news_url
                self.article_data_list.append(tmp_dict)
        data = souhu_change_char(self.article_data_list)
        insert_news_to_mysql(data)


if __name__ == '__main__':
    souhu = SouhuSpider('2016-1-26 12:30:00')
    souhu.main()
