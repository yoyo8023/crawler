# coding:utf8


def char_change_gbk(data):
    return data.encode('unicode-escape').decode('string-escape').decode('gbk', 'ignore')


def char_change_utf8(data):
    return data.decode('string-escape').decode('utf-8')


def sina_char_change_utf8(data):
    return data.encode('unicode-escape').decode('string-escape').decode('utf8', 'ignore')


def auto_char_change(data, char_type):
    return data.decode(char_type, 'ignore')


def char_change_ascii(data):
    return data.encode('unicode-escape').decode('string-escape').decode('ascii', 'ignore')
