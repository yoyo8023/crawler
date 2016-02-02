# coding:utf8


def char_change_gbk(data):
    return data.encode('unicode-escape').decode('string-escape').decode('gbk', 'ignore')


def char_change_utf8(data):
    return data.encode('unicode-escape').decode('string-escape').decode('utf8', 'ignore')
