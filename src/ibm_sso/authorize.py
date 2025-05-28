import os
import random
import string
from urllib.parse import urlencode

from authlib.integrations.base_client.errors import (
    InvalidTokenError,
    MismatchingStateError,
    OAuthError,
)
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client.apps import StarletteOAuth2App
from authlib.oidc.core.claims import UserInfo
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import HTTPStatusError
from requests.models import Response
from starlette import status
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from ibm_sso.dto.TokenDTO import IntrospectTokenDTO, RefreshTokenDTO, RevokeTokenDTO
from ibm_sso.vo.UserInfoVO import AuthorizeInfoVO, TokenInfoVO, UserInfoVO, UserInfoMiddleWareVO

authorize_router = APIRouter()

load_dotenv()

W3ID_CLIENT_ID = os.getenv("W3ID_CLIENT_ID")
W3ID_CLIENT_SECRET = os.getenv("W3ID_CLIENT_SECRET")

# Load configuration from environment
#
# If env_file is not specified, `.env` is used by default.
# If neither is specified, it will be read from the environment.
config = Config()

# Create an OAuth instance based on the configuration
oauth = OAuth(config)

# Register a remote application on the OAuth registry via oauth.register method.
#
# It will load W3ID_CLIENT_ID, W3ID_CLIENT_SECRET and other information starting with `W3ID_` from the environment.
# Where `W3ID` is the uppercase copy of the name specified in name param.
#
# In the `oauth.register` method, any information starting with `W3ID_` read from the environment will be copied to the oauth.register's kwargs.
w3id: StarletteOAuth2App = oauth.register(
    name="w3id",
    client_kwargs={
        # https://docs.authlib.org/en/latest/oauth/2/intro.html#client-authentication-methods
        # 'token_endpoint_auth_method': 'client_secret_basic',
        # 'token_placement': 'header',
        "scope": "openid profile email"
    },
)
# print(type(w3id))

# Creating an AsyncOAuth2Client instance
async_oauth2_client = AsyncOAuth2Client(
    client_id=W3ID_CLIENT_ID,
    client_secret=W3ID_CLIENT_SECRET,
    scope="openid profile email",
)


# async def get_oauth_client() -> AsyncOAuth2Client:
#     return AsyncOAuth2Client(
#         client_id=W3ID_CLIENT_ID,
#         client_secret=W3ID_CLIENT_SECRET,
#         scope='openid profile email',
#     )

# Swagger UI: Use the user input(Bearer Token)
security = HTTPBearer()


def __generate_state(length=32):
    """Used to generate state when manually managing state.

    If you don't manage state manually, you need to use OAuth2Session.
    When using OAuth2Session, there will be problems when running multiple instances, unless redis is introduced.

    In order to completely avoid session management, choose to manage state manually here
    """
    return "".join(
        random.choices(
            string.ascii_letters
            + string.digits
            + string.ascii_lowercase
            + string.ascii_uppercase,
            k=length,
        )
    )


def __get_access_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Get the Bearer token from the request header"""
    try:
        return credentials.credentials
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


async def get_current_user(access_token: str = Depends(__get_access_token)):
    """Get current user info.(Also protect RESTful API.)<br/><br/>

    W3ID SSO does not provide an API to check whether the token is expired,
    but only provides an API(introspect) to check whether the token is valid.
    Therefore, the token expiration check can be performed on the client side through `expires_at`
    """
    try:
        result: UserInfo = await w3id.userinfo(
            token={"access_token": access_token, "token_type": "Bearer"}
        )
        userInfoVO = UserInfoVO.model_validate(result)
        return userInfoVO
    except HTTPStatusError as e:
        raise InvalidTokenError()


async def get_current_user_for_middleware(request: Request):
    """Get current user info in FastAPI middleware.<br/><br/>

    In FastAPI middleware, you can't use `get_current_user` with Depends.
    If you need to access user information within middleware — for example, to log the currently authenticated user in access logs,
    you should use `get_current_user_for_middleware` instead.<br/><br/>

    Note: In production systems, you generally shouldn't use `get_current_user_for_middleware`. 
    Instead, you should store `user information` along with their `access_token` and `refresh_token` in `Redis`. 
    This approach can significantly improve access speed. <br/>
    The current implementation simply provides a solution that does not rely on Redis.
    """
    access_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not access_token:
        return UserInfoMiddleWareVO()
    try:
        result: UserInfo = await w3id.userinfo(
            token={"access_token": access_token, "token_type": "Bearer"}
        )
        userInfoVO = UserInfoMiddleWareVO.model_validate(result)
        return userInfoVO
    except HTTPException as e:
        return UserInfoMiddleWareVO()


@authorize_router.get(
    "/token",
    description="""Get an access token by code, state and nonce.<br/><br/>
        The code and state are the values returned by the SSO server after successful authentication.
        And nonce is a random value generated by the client and is the same value used in the authentication process.<br/><br/>
        Note:<br/>
        mismatching_state: The state is incorrect or has been used.<br/>
        invalid_grant: It may be that the debugging took too long, resulting in the inability to generate a token based on the code and state.<br/>
        If any of the above errors occur, you will need to re-authenticate.
        """,
    summary="Obtain an Access Token",
    response_model=AuthorizeInfoVO,
)
async def get_token(code: str, state: str, nonce: str, redirect_uri: str):
    metadata = await w3id.load_server_metadata()
    try:
        token = await async_oauth2_client.fetch_token(
            url=metadata["token_endpoint"],
            state=state,
            code=code,
            redirect_uri=redirect_uri,
        )

        user_info: UserInfo = await w3id.parse_id_token(token, nonce)
        user_info_vo = {
            **token,
            "userinfo": {
                "displayName": user_info["displayName"],
                "emailAddress": user_info["emailAddress"],
                "uid": user_info["uid"],
            },
        }
        return user_info_vo
    except MismatchingStateError as e:
        # If mismatching_state(The state is incorrect or has been used) occured
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The state is incorrect or has been used.",
        )
    except OAuthError:
        # If invalid_grant(CSIAQ0158E The [authorization_grant] of type [authorization_code] does not exist or is invalid) occured
        # It may be that the debugging took too long, resulting in the inability to generate a token based on the code and state.
        # Re-authentication is required
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_grant",
        )


@authorize_router.post(
    "/introspect",
    description="""Verify the validity and related information of an access token or refresh token.<br/><br/>
        👇<br/>
        In addition to verifying the validity of the token, 
        introspection can also obtain more information associated with the token, such as the token holder, scopes, generation time, etc.<br/>
        This is very useful for role-based access control and resource permission control.<br/><br/>
        <strong><i>
        W3ID SSO does not provide an API to check whether the token is expired, 
        but only provides an API(introspect) to check whether the token is valid.
        Therefore, the token expiration check can be performed on the client side through `expires_at`
        </i></strong>
        """,
    summary="Revoke access_token or refresh_token",
)
async def introspect_token(
    dto: IntrospectTokenDTO, _: UserInfoVO = Depends(get_current_user)
):
    metadata = await w3id.load_server_metadata()
    result: Response = await async_oauth2_client.introspect_token(
        metadata["introspection_endpoint"],
        token=dto.token,
    )

    return result.json()


@authorize_router.post(
    "/revoke",
    description="""Revoke access token or refresh token.<br/><br/>
        👇<br/>
        <strong><i>
        If the access token is revoked, the refresh token will not be revoked and can continue to be used.<br/>
        If the refresh token is revoked, the access token will also be revoked at the same time.
        </i></strong>
        """,
    summary="Revoke access_token or refresh_token",
)
async def revoke_token(dto: RevokeTokenDTO, _: UserInfoVO = Depends(get_current_user)):
    metadata = await w3id.load_server_metadata()
    res: Response = await async_oauth2_client.revoke_token(
        metadata["revocation_endpoint"],
        token=dto.token,
    )
    return JSONResponse(
        content={"content": res.content.decode("utf-8")}, status_code=res.status_code
    )


@authorize_router.post(
    "/refresh_token",
    description="Get a new access token by refresh_token.",
    summary="Refresh the Access Token",
    response_model=TokenInfoVO,
)
async def refresh_token(dto: RefreshTokenDTO):
    metadata = await w3id.load_server_metadata()
    try:
        result = await async_oauth2_client.refresh_token(
            metadata["token_endpoint"],
            refresh_token=dto.refresh_token,
        )
        return TokenInfoVO.model_validate(result)
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.error,
        )


@authorize_router.get(
    "/userinfo",
    description="Get user info.",
    summary="Get user info",
    response_model=UserInfoVO,
)
async def get_userinfo(user_info: UserInfoVO = Depends(get_current_user)):
    # curl -k GET 'https://localhost:5000/oauth2/userinfo' \
    # --header 'Authorization: Bearer access_token'
    return user_info


@authorize_router.get(
    "/login",
    description="""User login.<br/><br/>
        <strong><i>
        Login processing does not need to go through swagger,
        </i></strong>
        you can get code and state in the following ways.<br/>
        After getting the code and state, get the token information through the `/token` api.<br/><br/>
        👇<br/>
        For sso authentication, you can directly click 
        <a href='/oauth2/login?redirect_uri=https://localhost:3000/auth/callback&nonce=test' target='_blank'>Login with SSO</a>
        <br/>
        Note:<br>
        Generally, nonce is generated on the client side.
        """,
    summary="User login",
)
async def login(
    request: Request, redirect_uri: str = Query(...), nonce: str = Query(...)
):

    # # Use OAuth2Session
    # request.session['redirect'] = redirect_uri
    # redirect_uri = request.url_for('auth')
    # return await w3id.authorize_redirect(request, redirect_uri)

    # Manually generate random state to avoid using OAuth2Session
    state = __generate_state()

    # Build redirect uri
    metadata = await w3id.load_server_metadata()
    auth_uri = metadata["authorization_endpoint"]
    full_redirect_uri = f'{auth_uri}?{urlencode({"redirect_uri": redirect_uri})}'

    # Manually create the authorization URL.
    # Will contain code, state, nonce, redirect_uri parameters.
    authorization_url, _ = async_oauth2_client.create_authorization_url(
        full_redirect_uri,
        state=state,
        nonce=nonce,
    )

    # Jump to the SSO authentication page.
    # If the authentication is successful, it will jump to the redirect url, carrying code, state and nonce parameters.
    return RedirectResponse(url=authorization_url)


@authorize_router.get("/authorize", include_in_schema=False)
async def auth(redirect_uri: str, request: Request):
    """After successful authentication, obtain token information and return it to the client callback.<br/><br/>
    <br/>
    If you use OAuth2Session, you can use this endpoint. Refer to the following code in login function:
    ```python
    request.session['redirect'] = redirect

    redirect_uri = request.url_for('auth')
    return await w3id.authorize_redirect(request, redirect_uri)
    ```
    <br/><br/>
    The current version does not use this function because it does not use OAuth2Session but AsyncOAuth2Client.
    """
    try:
        token = await w3id.authorize_access_token(request)
    except OAuthError as error:
        if error.error == "mismatching_state" or error.error == "invalid_grant":
            # If errors like invalid_grant or mismatching_state occur, jump to the redirect url and re-authenticate.
            return RedirectResponse(url=redirect_uri)
        # Return error page
        return HTMLResponse(f"<h1>{error.error}</h1>")

    # user = token.get('userinfo')
    # if user:
    #     request.session['user'] = dict(user)

    # param = json.dumps(token)
    token_info = AuthorizeInfoVO.model_validate(token)
    return RedirectResponse(
        url=f"{redirect_uri}?response={token_info.model_dump_json()}"
    )
