#!/usr/bin/python3
# -*- coding:utf-8 -*-

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from ibm_sso.authorize import get_current_user
from ibm_sso.vo.UserInfoVO import UserInfoVO

sample_router = APIRouter()

security = HTTPBearer()


@sample_router.get('/noauth')
async def say_hello_to_guest():
    return 'Hello, Guest!'


@sample_router.get('/auth')
async def say_hello_to_user(user_info: UserInfoVO = Depends(get_current_user)):
    return f'Hello, {user_info.display_name}!'
