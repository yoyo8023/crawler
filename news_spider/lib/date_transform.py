import time


def string_transform_timestamp(time_str):
    return time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))


