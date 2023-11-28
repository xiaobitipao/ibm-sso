#!/usr/bin/python3
# -*- coding:utf-8 -*-

# https://shiriev.ru/pydantic-two-way-mapping/
# https://docs.pydantic.dev/latest/migration/#changes-to-dataclasses
# https://docs.pydantic.dev/latest/concepts/dataclasses/#dataclass-config
# https://docs.pydantic.dev/latest/migration/#changes-to-config
# https://www.youtube.com/watch?app=desktop&v=Z0a0Vjd992I

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass(config=dict(populate_by_name=True))
class UserInfoVO(BaseModel):
    display_name: str = Field(validation_alias='displayName')
    email_address: str = Field(validation_alias='emailAddress')
    uid: str


class TokenInfoVO(BaseModel):
    access_token: str
    refresh_token: str
    scope: str
    grant_id: str
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int


@dataclass(config=dict(populate_by_name=True))
class AuthorizeInfoVO(BaseModel):
    access_token: str
    refresh_token: str
    scope: str
    grant_id: str
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int
    user_info: UserInfoVO = Field(validation_alias='userinfo')


if __name__ == '__main__':
    data = {
        'displayName': 'displayName',
        'emailAddress': 'emailAddress',
        'uid': 'uid',
    }
    result = UserInfoVO.model_validate(data)
    print(result)
