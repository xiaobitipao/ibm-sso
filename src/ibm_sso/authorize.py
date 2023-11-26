import os

from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from ibm_sso.libs.logger import getLogger
from ibm_sso.service.sso_ibm_service import sso_ibm_get_user_info
from ibm_sso.vo.UserInfoVO import TokenInfoVO, UserInfoVO

authorize_router = APIRouter()

logger = getLogger(__name__)

load_dotenv()

W3ID_ENDPOINT_DISCOVERY = os.getenv('W3ID_ENDPOINT_DISCOVERY')

config = Config()
oauth = OAuth(config)

# from authlib.integrations.starlette_client.apps import StarletteOAuth2App
# class: authlib.integrations.starlette_client.apps.StarletteOAuth2App
w3id = oauth.register(
    name='w3id',
    server_metadata_url=W3ID_ENDPOINT_DISCOVERY,
    client_kwargs={
        'scope': 'openid email profile'
    }
)
print(type(w3id))


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
    logger.debug(f'credentials: {credentials.credentials}')
    return sso_ibm_get_user_info(credentials.credentials)


@authorize_router.get('/userinfo', response_model=UserInfoVO)
async def get_userinfo(user_info: dict = Depends(get_current_user)):
    # curl -k GET 'https://localhost:5000/oauth2/userinfo' \
    # --header 'Authorization: Bearer access_token'
    # result = sso_ibm_get_user_info(token)
    return UserInfoVO.model_validate(user_info)


@authorize_router.get('/login')
async def login(request: Request, redirect: str = Query(...)):

    request.session['redirect'] = redirect

    redirect_uri = request.url_for('auth')
    return await oauth.w3id.authorize_redirect(request, redirect_uri)


@authorize_router.get('/authorize')
async def auth(request: Request):
    try:
        token = await oauth.w3id.authorize_access_token(request)
    except OAuthError as error:
        # TODO: Error page
        return HTMLResponse(f'<h1>{error.error}</h1>')

    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)

    # param = json.dumps(token)
    token_info = TokenInfoVO.model_validate(token)
    redirect = request.session['redirect']
    return RedirectResponse(url=f'{redirect}?response={token_info.model_dump_json()}')
