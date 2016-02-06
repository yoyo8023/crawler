# coding:utf8
import os
import traceback
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from conf.settings import LOG_DIR
from lib.char_change import char_change_gbk
from lib.date_transform import string_transform_timestamp
from lib.mysql_api import insert_news_to_mysql
from lib.oss_api import upload_img_to_oss2
from lib.source_html import get_tag_html

import logging
logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_DIR + 'souhu.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


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

    def get_content(self, url):
        data_content = requests.get(url, timeout=3).text
        return char_change_gbk(data_content)

    def detail_spider(self, url):
        content = self.get_content(url)
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
                news_body = self.get_content(news)
            except Exception as e:
                logger.debug(traceback.format_exc())
                continue
            news_soup = BeautifulSoup(news_body)
            if 'pic' not in news:
                print news
                title = get_tag_html(news_soup, 'h1')
                tmp_dict['title'] = title
                # 获取图片
                img_list = list()
                img_tag = u'<div><img alt="{img_title}" src="{img_url}"><span>{img_title}</span></div>'
                artile = ''
                for img in news_soup.select("#contentText img"):
                    img_title = img['alt']
                    img_url = img['src']
                    # 上传图片到阿里云
                    status, msg, img_url = upload_img_to_oss2(img_url)
                    if status:
                        img_list.append([img_title, img_url])
                        artile += img_tag.format(img_url=img_url, img_title=img_title)
                # 获取文章内容
                for a in news_soup.select("#contentText p"):
                    for string in a.strings:
                        if '_tvId' not in string:
                            artile += u'<p>' + string.strip() + u'</p>'
                artile = artile.replace(u'搜狐娱乐讯 ', '')
                tmp_dict['artile'] = artile
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
                        img_list.append([img_title, img_url])
                tmp_dict['img_list'] = img_list
                tmp_dict['pic_mode'] = 1
            tmp_dict['source'] = news
            self.article_data_list.append(tmp_dict)

    def main(self):
        for url in self.url_list:
            new_url = url.format(page='')
            try:
                content = self.get_content(new_url)
            except Exception as e:
                logger.debug(traceback.format_exc())
                continue
            # 获取max page
            content_list = content.split('\n')
            max_page = 0
            for c in content_list:
                if 'var maxPage = ' in c:
                    start_index = c.find('=') + 1
                    max_page = int(c[start_index: -1].strip()) - 1
                    break
            try:
                self.detail_spider(url)
            except Exception as e:
                logger.debug(traceback.format_exc())
                continue
            while self.flag != 1 and max_page != 0:
                max_page_str = '_' + str(max_page)
                print url.format(page=max_page_str)
                try:
                    self.detail_spider(url.format(page=max_page_str))
                except Exception as e:
                    logger.debug(traceback.format_exc())
                    continue
                max_page -= 1
            self.flag = 0
        print self.article_data_list
        insert_news_to_mysql(self.article_data_list)

    def pic_main(self):
        for url in self.pic_url_list:
            try:
                content = self.get_content(url)
            except Exception as e:
                logger.debug(traceback.format_exc())
                continue
            soup = BeautifulSoup(content)
            for data in soup.select("#item-list a"):
                tmp_dict = dict()
                news_url = data['href']
                try:
                    news_body = self.get_content(news_url)
                except Exception as e:
                    logger.debug(traceback.format_exc())
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
                        img_list.append([img_title, img_url])
                tmp_dict['img_list'] = img_list
                tmp_dict['source'] = news_url
                self.article_data_list.append(tmp_dict)
        insert_news_to_mysql(self.article_data_list)


if __name__ == '__main__':
    souhu = SouhuSpider('2016-1-29 11:30:00')
    souhu.main()
