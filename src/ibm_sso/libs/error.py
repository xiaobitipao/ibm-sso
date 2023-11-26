#!/usr/bin/python3
# -*- coding:utf-8 -*-

from fastapi import HTTPException
from starlette import status


class APIException(HTTPException):

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Internal Server Error!'
    headers = None

    def __init__(self, status_code=None, detail=None, headers=None):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = detail
        if headers:
            self.headers = headers
        super(APIException, self).__init__(
            self.status_code, self.detail, self.headers)


class ParameterException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Invalid Parameter'


class AuthException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Authorization Failed'


class ForbiddenException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Forbidden Error!'
