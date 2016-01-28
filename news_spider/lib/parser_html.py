# coding:utf8
from HTMLParser import HTMLParser


def strip_tags(html):
    try:
        html = html.strip()
        result = []
        parse = HTMLParser()
        parse.handle_data = result.append
        parse.feed(html)
        parse.close()
        return "".join(result)
    except Exception as e:
        print e
        return ''
