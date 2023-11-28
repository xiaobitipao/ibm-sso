import os

import requests
from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
from starlette import status

load_dotenv()

W3ID_USER_INFO_URL = os.getenv('W3ID_USER_INFO_URL')
W3ID_CLIENT_ID = os.getenv('W3ID_CLIENT_ID')
W3ID_CLIENT_SECRET = os.getenv('W3ID_CLIENT_SECRET')
W3ID_ENDPOINT_INTROSPECT = os.getenv('W3ID_ENDPOINT_INTROSPECT')
W3ID_ACCESS_TOKEN_URL = os.getenv('W3ID_ACCESS_TOKEN_URL')


# TODO: CSIAQ0158E The [authorization_grant] of type [authorization_code] does not exist or is invalid.
# def sso_ibm_get_access_token_by_code(code: str, redirect_uri: str):
#     '''Get access token by code.'''

#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#     }

#     form_data = {
#         'code': code,
#         'grant_type': 'authorization_code',
#         'client_id': W3ID_CLIENT_ID,
#         'client_secret': W3ID_CLIENT_SECRET,
#         'redirect_uri': redirect_uri,
#     }
#     data = '&'.join([f'{key}={value}' for key, value in form_data.items()])

#     response = requests.post(
#         W3ID_ACCESS_TOKEN_URL,
#         headers=headers,
#         data=data,
#     )

#     result = response.json()
#     if (response.status_code == status.HTTP_200_OK):
#         return result
#     else:
#         raise OAuthError(error=result['error_description'])


def sso_ibm_refresh_access_token_by_refresh_token(refresh_token: str):
    '''Refresh access token by refresh token.'''

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    form_data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': W3ID_CLIENT_ID,
        'client_secret': W3ID_CLIENT_SECRET,
    }
    data = '&'.join([f'{key}={value}' for key, value in form_data.items()])

    response = requests.post(
        W3ID_ACCESS_TOKEN_URL,
        headers=headers,
        data=data,
    )

    result = response.json()
    if (response.status_code == status.HTTP_200_OK):
        return result
    else:
        raise OAuthError(error=result['error'])


def sso_ibm_get_user_info(access_token: str):
    '''Get userinfo by access token'''

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    form_data = {
        'access_token': access_token,
        'client_id': W3ID_CLIENT_ID,
        'client_secret': W3ID_CLIENT_SECRET,
    }
    data = '&'.join([f'{key}={value}' for key, value in form_data.items()])

    response = requests.post(
        W3ID_USER_INFO_URL,
        headers=headers,
        data=data,
    )

    result = response.json()
    if (response.status_code == status.HTTP_200_OK):
        return result
    else:
        raise OAuthError(error=result['error'])


def sso_ibm_verify_access_token(access_token: str):
    '''Verify access token'''

    # curl POST 'https://preprod.login.w3.ibm.com/oidc/endpoint/default/introspect' \
    # --header 'Content-Type: application/x-www-form-urlencoded' \
    # --data 'token=aaa&client_id=aaa&client_secret=aaa'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    form_data = {
        'token': access_token,
        'client_id': W3ID_CLIENT_ID,
        'client_secret': W3ID_CLIENT_SECRET,
    }
    data = '&'.join([f'{key}={value}' for key, value in form_data.items()])

    response = requests.post(
        W3ID_ENDPOINT_INTROSPECT,
        headers=headers,
        data=data,
    )

    result = response.json()
    if (response.status_code == status.HTTP_200_OK):
        if not result['active']:
            raise OAuthError(error=result['error'])
    else:
        raise OAuthError(error=result['error'])
