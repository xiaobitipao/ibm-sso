#!/usr/bin/python3
# -*- coding:utf-8 -*-

from pydantic import BaseModel


class TokenDTO(BaseModel):

    code: str

    redirect_uri: str
