#!/usr/bin/python3
# -*- coding:utf-8 -*-

from enum import Enum


class TokenTypeHintEnum(str, Enum):
    access_token = 'access_token'
    refresh_token = 'refresh_token'
