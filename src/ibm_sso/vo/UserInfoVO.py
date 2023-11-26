#!/usr/bin/python3
# -*- coding:utf-8 -*-

# https://shiriev.ru/pydantic-two-way-mapping/
# https://docs.pydantic.dev/latest/migration/#changes-to-config
# https://www.youtube.com/watch?app=desktop&v=Z0a0Vjd992I

from pydantic import BaseModel, Field


class UserInfoVO(BaseModel):
    display_name: str = Field(alias='displayName')
    email_address: str = Field(alias='emailAddress')
    uid: str


class TokenInfoVO(BaseModel):
    access_token: str
    refresh_token: str
    id_token: str
    scope: str
    grant_id: str
    token_type: str
    expires_in: int
    expires_at: int
    user_info: UserInfoVO = Field(alias='userinfo')
