#!/usr/bin/python3
# -*- coding:utf-8 -*-

import requests
from fastapi import HTTPException
from starlette import status


def read_remote_json_file(url):
    response = requests.get(url)
    result = response.json()
    if response.status_code == status.HTTP_200_OK:
        return result
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=result['error'],
    )
