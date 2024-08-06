# https://shiriev.ru/pydantic-two-way-mapping/
# https://docs.pydantic.dev/latest/migration/#changes-to-dataclasses
# https://docs.pydantic.dev/latest/concepts/dataclasses/#dataclass-config
# https://docs.pydantic.dev/latest/migration/#changes-to-config
# https://www.youtube.com/watch?app=desktop&v=Z0a0Vjd992I

from typing import Optional

from pydantic import BaseModel, Field
from util.const import AVATAR_PREFIX


class UserInfoVO(BaseModel):
    display_name: str = Field(alias='displayName')
    email_address: str = Field(alias='emailAddress')
    uid: str
    avatar: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.avatar = AVATAR_PREFIX + self.uid


class TokenInfoVO(BaseModel):
    access_token: str
    refresh_token: str
    scope: str
    grant_id: str
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int


class AuthorizeInfoVO(BaseModel):
    access_token: str
    refresh_token: str
    scope: str
    grant_id: str
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int
    user_info: UserInfoVO = Field(alias='userinfo')


if __name__ == '__main__':
    data = {
        'displayName': 'displayName',
        'emailAddress': 'emailAddress',
        'uid': 'uid',
    }
    result = UserInfoVO.model_validate(data)
    print(result)

    print('========================================================================')

    data = {
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'scope': 'scope',
        'grant_id': 'grant_id',
        'id_token': 'id_token',
        'token_type': 'token_type',
        'expires_in': 3600,
        'expires_at': 1609459200,
        'userinfo': {
            'displayName': 'displayName',
            'emailAddress': 'emailAddress',
            'uid': 'uid',
        }

    }
    result = AuthorizeInfoVO.model_validate(data)
    print(result)
