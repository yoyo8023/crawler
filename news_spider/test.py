# coding:utf8

import sys
import chardet

from conf.settings import LOG_DIR

rawdata = 'Wahaha\xef\xbc\x88\xe4\xb8\xa4\xe6\x98\x9f\xe6\x9c\x9f\xe8\xbf\x87\xe5\xbe\x97\xe5\xbe\x88\xe5\xbf\xab'

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
