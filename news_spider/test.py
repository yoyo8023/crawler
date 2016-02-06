# coding:utf8

import sys
import chardet

from conf.settings import LOG_DIR

rawdata = 'S LIFE\xe2\x80\x9d\xe6\xbc\x94\xe5\x94\xb1\xe4\xbc\x9a\xef\xbc\x8c\xe5\xb0\x86\xe5\x9c\xa84\xe6\x9c\x881\xe6\x97\xa5\xe5\x88\xb04\xe6\x9c\x883\xe6\x97\xa5\xe4\xba\x8e\xe5\x8f\xb0\xe5\x8c\x97\xe5\xb0\x8f\xe5\xb7\xa8\xe8\x9b\x8b\xe4\xb8\xbe\xe8\xa1\x8c\xef\xbc\x8c\xe5\x94\xae\xe7\xa5\xa8'

print chardet.detect(rawdata)

print rawdata.decode('utf8', 'ignore')

import logging

logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_DIR + 'test.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
