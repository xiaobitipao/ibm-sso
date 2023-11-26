#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s')

# Use FileHandler to output file
# fh = logging.FileHandler('log-ibmsso.log')
# fh.setLevel(logging.INFO)
# fh.setFormatter(formatter)

# Use StreamHandler to output console
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)


def getLogger(name):

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    logger.addHandler(sh)
    # logger.addHandler(fh)

    return logger
