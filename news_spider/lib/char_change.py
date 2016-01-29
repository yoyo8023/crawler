# coding:utf8
from requests.packages import chardet


def char_change_gbk(data):
    return data.encode('unicode-escape').decode('string-escape').decode('gbk', 'ignore')


def char_change_utf8(data):
    return data.encode('unicode-escape').decode('string-escape').decode('utf8', 'ignore')


def char_change_ascii(data):
    print data.encode('unicode-escape').decode('string-escape').decode('gbk', 'ignore')
    return data.encode('unicode-escape').decode('string-escape').decode('gbk', 'ignore')


def sina_change_char(data_list):
    for index, data in enumerate(data_list):
        for key in data.keys():
            if isinstance(data[key], list):
                for img_index, img in enumerate(data[key]):
                    data_list[index][key][img_index][0] = char_change_utf8(img[0])
                    data_list[index][key][img_index][1] = char_change_utf8(img[1])
            else:
                try:
                    data_list[index][key] = char_change_utf8(data[key])
                    if key == 'artile':
                        data_list[index][key] = data_list[index][key].replace(u'新浪娱乐讯 ', '')
                        data_list[index][key] = data_list[index][key].replace(u'<p>[微博]</p>', '')
                except Exception as e:
                    print e
    return data_list


def souhu_change_char(data_list):
    for index, data in enumerate(data_list):
        print data
        for key in data.keys():
            if isinstance(data[key], list):
                for img_index, img in enumerate(data[key]):
                    data_list[index][key][img_index][0] = char_change_gbk(img[0])
                    data_list[index][key][img_index][1] = char_change_gbk(img[1])
            else:
                try:
                    data_list[index][key] = char_change_gbk(data[key])
                    if key == 'artile':
                        data_list[index][key] = data_list[index][key].replace(u'搜狐娱乐讯 ', '')
                except Exception as e:
                    print e
    return data_list


def ifeng_change_char(data_list):
    for index, data in enumerate(data_list):
        print data
        for key in data.keys():
            if isinstance(data[key], list):
                for img_index, img in enumerate(data[key]):
                    data_list[index][key][img_index][0] = char_change_ascii(img[0])
                    data_list[index][key][img_index][1] = char_change_ascii(img[1])
            else:
                try:
                    data_list[index][key] = char_change_ascii(data[key])
                except Exception as e:
                    print e
    return data_list
