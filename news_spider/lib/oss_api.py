# -*- coding: utf-8 -*-

import uuid
from datetime import datetime

import oss2
import requests

from conf import settings


def get_today_datestr():
    now_date = datetime.now()
    return now_date.strftime('%Y%m%d')


def upload_img_to_oss2(img_url):
    try:
        auth = oss2.Auth(settings.OSS['ACCESSKEYID'], settings.OSS['ACCESSKEYSECRET'])
        bucket = oss2.Bucket(auth, settings.OSS['ENDPOINT'], settings.OSS['BUCKET_NAME'])
        input_img = requests.get(img_url)
        img_name = u'hcmcrawler/news/'+get_today_datestr()+'/'+str(uuid.uuid4()) + '.' + img_url.split('.')[-1]
        bucket.put_object(img_name, input_img)
        return True, 'ok', settings.OSS['STATIC_URL'] + img_name
    except Exception as e:
        return False, e.message, ''


if __name__ == '__main__':
    print upload_img_to_oss2('http://n.sinaimg.cn/ent/transform/20160118/ZvES-fxnqriz9813983.jpg')
