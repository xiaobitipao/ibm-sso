import os

from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from ibm_sso.service.sso_ibm_service import sso_ibm_get_user_info
from ibm_sso.vo.UserInfoVO import AuthorizeInfoVO, TokenInfoVO, UserInfoVO

authorize_router = APIRouter()

load_dotenv()

W3ID_CLIENT_ID = os.getenv('W3ID_CLIENT_ID')
W3ID_CLIENT_SECRET = os.getenv('W3ID_CLIENT_SECRET')
W3ID_ACCESS_TOKEN_URL = os.getenv('W3ID_ACCESS_TOKEN_URL')
W3ID_ENDPOINT_DISCOVERY = os.getenv('W3ID_ENDPOINT_DISCOVERY')
W3ID_ENDPOINT_REVOCATION = os.getenv('W3ID_ENDPOINT_REVOCATION')

# Get environment variable information by default
config = Config()

# Create an authentication server instance based on the configuration
#
# from authlib.integrations.starlette_client.apps import StarletteOAuth2App
# class: authlib.integrations.starlette_client.apps.StarletteOAuth2App
oauth = OAuth(config)
w3id = oauth.register(
    name='w3id',
    server_metadata_url=W3ID_ENDPOINT_DISCOVERY,
    client_kwargs={
        'scope': 'openid profile email'
    }
)
# print(type(w3id))

# Create OAuth2Session instance
oauth2_session = OAuth2Session(
    W3ID_CLIENT_ID,
    W3ID_CLIENT_SECRET,
    scope='openid',
)


# #########################################################################################
# Swagger UI: Use the user input(username/password) to perform login processing through the endpoint(/token)
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     '''Protect RESTful API'''
#     # sso_ibm_verify_access_token(token)
#     # return token
#     user_info = sso_ibm_get_user_info(token)
#     return user_info

# #########################################################################################
# Swagger UI: Use the user input(Bearer Token)
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    '''Protect RESTful API'''
    result = sso_ibm_get_user_info(credentials.credentials)
    return UserInfoVO.model_validate(result)


# TODO: CSIAQ0158E The [authorization_grant] of type [authorization_code] does not exist or is invalid.
# @authorize_router.post('/token', description='Get an access token by code.', summary='Obtain an Access Token', response_model=TokenInfoVO)
# async def get_token(dto: TokenDTO):
#     result = sso_ibm_get_access_token_by_code(dto.code, dto.redirect_uri)
#     return TokenInfoVO.model_validate(result)


@authorize_router.post(
    '/revoke',
    description='''Revoke access_token or refresh_token.<br/><br/>
        👇<br/>
        <strong><i>
        If the access token is revoked, the refresh token will not be revoked and can continue to be used.<br/>
        If the refresh token is revoked, the access token will also be revoked at the same time.
        </i></strong>
        ''',
    summary='Revoke access_token or refresh_token'
)
async def revoke_token(token: str):
    result = oauth2_session.revoke_token(
        W3ID_ENDPOINT_REVOCATION,
        # token_type_hint=token_type_hint.value,
        token=token,
    )
    return result.reason


@authorize_router.post(
    '/refresh_token',
    description='Get an new access token by refresh_token.',
    summary='Refresh the Access Token',
    response_model=TokenInfoVO
)
async def refresh_token(refresh_token: str):
    # result = sso_ibm_refresh_access_token_by_refresh_token(refresh_token)
    result = oauth2_session.refresh_token(
        W3ID_ACCESS_TOKEN_URL,
        refresh_token=refresh_token,
    )
    return TokenInfoVO.model_validate(result)


@authorize_router.get(
    '/userinfo',
    description='''Get user info.<br/><br/>
        👇<br/>
        <strong><i>
        For sso authentication, you can directly click 
        <a href='https://localhost:5000/oauth2/login?redirect=https://localhost:3000/example' target='_blank'>Login with SSO</a>
        </i></strong>
        ''',
    summary='Get user info',
    response_model=UserInfoVO
)
async def get_userinfo(user_info: UserInfoVO = Depends(get_current_user)):
    # curl -k GET 'https://localhost:5000/oauth2/userinfo' \
    # --header 'Authorization: Bearer access_token'
    # result = sso_ibm_get_user_info(token)
    return user_info


@authorize_router.get('/login', include_in_schema=False)
async def login(request: Request, redirect: str = Query(...)):

    request.session['redirect'] = redirect

    redirect_uri = request.url_for('auth')
    return await w3id.authorize_redirect(request, redirect_uri)


@authorize_router.get('/authorize', include_in_schema=False)
async def auth(request: Request):
    try:
        token = await w3id.authorize_access_token(request)
    except OAuthError as error:
        # TODO: Error page
        return HTMLResponse(f'<h1>{error.error}</h1>')

    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)

    # param = json.dumps(token)
    token_info = AuthorizeInfoVO.model_validate(token)
    redirect = request.session['redirect']
    return RedirectResponse(url=f'{redirect}?response={token_info.model_dump_json()}')
