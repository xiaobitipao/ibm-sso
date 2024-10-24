from pydantic import BaseModel


class IntrospectTokenDTO(BaseModel):
    token: str


class RevokeTokenDTO(BaseModel):
    token: str


class RefreshTokenDTO(BaseModel):
    refresh_token: str
