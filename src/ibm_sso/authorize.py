import os
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import (InvalidTokenError,
                                                     MismatchingStateError,
                                                     OAuthError)
from authlib.integrations.requests_client import OAuth2Session
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from authlib.oidc.core.claims import UserInfo
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import HTTPStatusError
from requests.models import Response
from starlette import status
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ibm_sso.vo.UserInfoVO import AuthorizeInfoVO, TokenInfoVO, UserInfoVO

authorize_router = APIRouter()

load_dotenv()

W3ID_CLIENT_ID = os.getenv('W3ID_CLIENT_ID')
W3ID_CLIENT_SECRET = os.getenv('W3ID_CLIENT_SECRET')
W3ID_ENDPOINT_DISCOVERY = os.getenv('W3ID_ENDPOINT_DISCOVERY')

# Get environment variable information by default(.env)
config = Config()

# Create an authentication server instance based on the configuration
#
# from authlib.integrations.starlette_client.apps import StarletteOAuth2App
# class: authlib.integrations.starlette_client.apps.StarletteOAuth2App
oauth = OAuth(config)
w3id: StarletteOAuth2App = oauth.register(
    name='w3id',
    server_metadata_url=W3ID_ENDPOINT_DISCOVERY,
    client_kwargs={
        'scope': 'openid profile email'
    }
)
# print(type(w3id))

# Create OAuth2Session instance
oauth2_session = OAuth2Session(
    client_id=W3ID_CLIENT_ID,
    client_secret=W3ID_CLIENT_SECRET,
    scope='openid',
)

# Swagger UI: Use the user input(Bearer Token)
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    '''Protect RESTful API.<br/><br/>
    W3ID SSO does not provide an API to check whether the token is expired, 
    but only provides an API(introspect) to check whether the token is valid.
    Therefore, the token expiration check can be performed on the client side through `expires_at`
    '''
    try:
        result: UserInfo = await w3id.userinfo(token={
            'access_token': credentials.credentials,
            'token_type': 'Bearer'
        })
        userInfoVO = UserInfoVO.model_validate(result)
        return userInfoVO
    except HTTPStatusError as e:
        error = e.response.json()
        raise InvalidTokenError(error=error['error'])


@authorize_router.get(
    '/token',
    description='''Get an access token by code.<br/><br/>
        mismatching_state: The state is incorrect or has been used.<br/>
        invalid_grant: It may be that the debugging took too long, resulting in the inability to generate a token based on the code and state.<br/>
        If any of the above errors occur, you will need to re-authenticate.
        ''',
    summary='Obtain an Access Token',
    response_model=AuthorizeInfoVO)
async def get_token(code: str, state: str, request: Request):
    try:
        # The query parameters code and state will be used in `w3id.authorize_access_token`.
        token = await w3id.authorize_access_token(request)
        token_info = AuthorizeInfoVO.model_validate(token)
        return token_info
    except OAuthError as error:
        if isinstance(error, MismatchingStateError):
            # If mismatching_state(The state is incorrect or has been used) occured
            return JSONResponse(content={'detail': error.error}, status_code=status.HTTP_400_BAD_REQUEST)
        elif error.error == 'invalid_grant':
            # If invalid_grant(CSIAQ0158E The [authorization_grant] of type [authorization_code] does not exist or is invalid) occured
            # It may be that the debugging took too long, resulting in the inability to generate a token based on the code and state.
            # Re-authentication is required
            return JSONResponse(content={'detail': error.error}, status_code=status.HTTP_400_BAD_REQUEST)
        raise error


@authorize_router.post(
    '/introspect',
    description='''Verify the validity and related information of an access token or refresh token.<br/><br/>
        👇<br/>
        In addition to verifying the validity of the token, 
        introspection can also obtain more information associated with the token, such as the token holder, scopes, generation time, etc.<br/>
        This is very useful for role-based access control and resource permission control.<br/><br/>
        <strong><i>
        W3ID SSO does not provide an API to check whether the token is expired, 
        but only provides an API(introspect) to check whether the token is valid.
        Therefore, the token expiration check can be performed on the client side through `expires_at`
        </i></strong>
        ''',
    summary='Revoke access_token or refresh_token'
)
async def introspect_token(token: str, _: UserInfoVO = Depends(get_current_user)):
    metadata = await w3id.load_server_metadata()
    result: Response = oauth2_session.introspect_token(
        metadata['introspection_endpoint'],
        token=token,
    )
    return result.json()


@authorize_router.post(
    '/revoke',
    description='''Revoke access token or refresh token.<br/><br/>
        👇<br/>
        <strong><i>
        If the access token is revoked, the refresh token will not be revoked and can continue to be used.<br/>
        If the refresh token is revoked, the access token will also be revoked at the same time.
        </i></strong>
        ''',
    summary='Revoke access_token or refresh_token'
)
async def revoke_token(token: str, _: UserInfoVO = Depends(get_current_user)):
    metadata = await w3id.load_server_metadata()
    result: Response = oauth2_session.revoke_token(
        metadata['revocation_endpoint'],
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
    metadata = await w3id.load_server_metadata()
    result = oauth2_session.refresh_token(
        metadata['token_endpoint'],
        refresh_token=refresh_token,
    )
    return TokenInfoVO.model_validate(result)


@authorize_router.get('/userinfo', description='Get user info.', summary='Get user info', response_model=UserInfoVO)
async def get_userinfo(user_info: UserInfoVO = Depends(get_current_user)):
    # curl -k GET 'https://localhost:5000/oauth2/userinfo' \
    # --header 'Authorization: Bearer access_token'
    return user_info


@authorize_router.get(
    '/login',
    description='''User login.<br/><br/>
        <strong><i>
        Login processing does not need to go through swagger,
        </i></strong>
        you can get code and state in the following ways.<br/>
        After getting the code and state, get the token information through the `/token` api.<br/><br/>
        👇<br/>
        For sso authentication, you can directly click 
        <a href='/oauth2/login?redirect=https://localhost:3000' target='_blank'>Login with SSO</a>
        ''',
    summary='User login')
async def login(request: Request, redirect: str = Query(...)):

    query_params = {'redirect': redirect}

    redirect_uri = request.url_for('auth')
    full_redirect_uri = f'{redirect_uri}?{urlencode(query_params)}'

    return await w3id.authorize_redirect(request, full_redirect_uri)


@authorize_router.get('/authorize', include_in_schema=False)
async def auth(redirect: str, request: Request):
    # # #######
    # # Return token instead of code, which is not safe
    # try:
    #     token = await w3id.authorize_access_token(request)
    # except OAuthError as error:
    #     if error.error == 'mismatching_state' or error.error == 'invalid_grant':
    #         # If errors like invalid_grant or mismatching_state occur, jump to the redirect url and re-authenticate.
    #         return RedirectResponse(url=redirect)
    #     # Return error page
    #     return HTMLResponse(f'<h1>{error.error}</h1>')

    # # user = token.get('userinfo')
    # # if user:
    # #     request.session['user'] = dict(user)

    # # param = json.dumps(token)
    # token_info = AuthorizeInfoVO.model_validate(token)
    # return RedirectResponse(url=f'{redirect}?response={token_info.model_dump_json()}')

    # #######
    # Returns code and state.
    # The front-end uses these two values ​​to obtain the token through the /token api
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    return RedirectResponse(url=f'{redirect}?code={code}&state={state}')
