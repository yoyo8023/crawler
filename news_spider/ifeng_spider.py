# coding:utf8
import os
import urllib
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from lib.date_transform import string_transform_timestamp
from lib.mysql_api import insert_news_to_mysql
from lib.oss_api import upload_img_to_oss2
from lib.source_html import get_tag_html

import logging
import logging.config

logging.config.fileConfig(os.path.join(os.path.abspath('.'), 'conf', "logging.conf"))
logger = logging.getLogger("example01")


class IFengSpider(object):
    """
    凤凰数据抓取
    :param url: 抓取数据的url
    :param start_time: 开始时间
    :param end_time: 结束时间
    """

    def __init__(self, url, start_time, end_time):
        self.url = url
        self.start_timestamp = string_transform_timestamp(start_time)
        self.end_timestamp = string_transform_timestamp(end_time)
        self.flag = 0
        self.article_data_list = list()
        self.url_list = [
            'http://ent.ifeng.com/listpage/3/{page}/list.shtml',
            'http://ent.ifeng.com/listpage/6/{page}/list.shtml',
            'http://ent.ifeng.com/listpage/1370/{page}/list.shtml',
            'http://ent.ifeng.com/listpage/30741/{page}/list.shtml',
        ]
        self.pic_url_list = [
            'http://yue.ifeng.com/pagelist/21897/{page}/list.shtml',
            'http://ent.ifeng.com/listpage/39788/{page}/list.shtml'
        ]

    def detail_spider(self, url):
        content = requests.get(url, timeout=3).text
        soup = BeautifulSoup(content)
        news_detail_list = list()
        for data in soup.select(".box_txt"):
            pub_timestamp = string_transform_timestamp(data.span.string + ':00')
            if pub_timestamp < self.start_timestamp or pub_timestamp > self.end_timestamp:
                self.flag = 1
                break
            news_detail_list.append(data.a['href'])
        for news in news_detail_list:
            print news
            tmp_dict = dict()
            try:
                news_body = requests.get(news, timeout=3).text
            except Exception, info:
                logger.info("news_url %s" % news)
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            news_soup = BeautifulSoup(news_body)
            title = get_tag_html(news_soup, 'h1')
            tmp_dict['title'] = title
            print title
            # 获取文章内容
            artile = ''
            for a in news_soup.select("#main_content p"):
                for string in a.strings:
                    artile += string.strip()
            tmp_dict['artile'] = artile
            print artile
            # 获取图片
            img_list = list()
            for data in news_soup.select("#main_content"):
                img_title = data.span.string
                img_url = data.p.img['src']
                # 上传图片到阿里云
                status, msg, img_url = upload_img_to_oss2(img_url)
                if status:
                    img_list.append([img_title, img_url])
            tmp_dict['img_list'] = img_list
            tmp_dict['source'] = news
            tmp_dict['pic_mode'] = 1
            self.article_data_list.append(tmp_dict)

    def pic_detail_spider(self, url):
        content = requests.get(url, timeout=3).text
        soup = BeautifulSoup(content)
        news_detail_list = list()
        now_year = str(datetime.now().year)
        for data in soup.select(".picList div"):
            if '(' in data.span.string:
                date_time = now_year + '-' + data.span.string[2:-1].replace('/', '-') + ':00'
            else:
                date_time = data.span.string + ':00'
            pub_timestamp = string_transform_timestamp(date_time)
            if pub_timestamp < self.start_timestamp or pub_timestamp > self.end_timestamp:
                self.flag = 1
                break
            news_detail_list.append(data.p.a['href'])
        for news in news_detail_list:
            print news
            tmp_dict = dict()
            try:
                news_body = requests.get(news, timeout=3).text
            except Exception, info:
                logger.info("news_url %s" % news)
                logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                continue
            news_soup = BeautifulSoup(news_body)
            title = get_tag_html(news_soup, 'h1')
            tmp_dict['title'] = title
            # 获取文章内容
            artile = ''
            content_list = news_body.split('\n')
            artile_list = list()
            img_list = list()
            for em in content_list:
                if '{title:' in em:
                    em = em.replace("{title:'", "")
                    em = em.replace("',", "")
                    artile_list.append(em.strip())
                if 'big_img: ' in em:
                    em = em.replace("big_img: '", "")
                    em = em.replace("',", "")
                    img_title = ''
                    # 上传图片到阿里云
                    status, msg, img_url = upload_img_to_oss2(em.strip())
                    if status:
                        img_list.append((img_title, img_url))
            for content in set(artile_list):
                artile += content
            tmp_dict['artile'] = artile
            tmp_dict['img_list'] = img_list
            tmp_dict['source'] = news
            tmp_dict['pic_mode'] = 1
            self.article_data_list.append(tmp_dict)

    def main(self):
        for url in self.url_list:
            page = 1
            while self.flag != 1:
                news_url = url.format(page=page)
                print news_url
                try:
                    self.detail_spider(news_url)
                except Exception, info:
                    logger.info("news_url %s" % news_url)
                    logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                page += 1
            self.flag = 0
        insert_news_to_mysql(self.article_data_list)

    def pic_main(self):
        for url in self.pic_url_list:
            page = 1
            print page
            while self.flag != 1:
                news_url = url.format(page=page)
                try:
                    self.pic_detail_spider(news_url)
                except Exception, info:
                    logger.debug("Error '%s' happened on line %d" % (info[0], info[1][1]))
                page += 1
            self.flag = 0
        insert_news_to_mysql(self.article_data_list)


if __name__ == '__main__':
    income_url = 'http://yule.sohu.com/tv.shtml'
    souhu = IFengSpider(income_url, '2016-1-20 00:00:00', '2016-1-21 23:59:59')
    souhu.main()
