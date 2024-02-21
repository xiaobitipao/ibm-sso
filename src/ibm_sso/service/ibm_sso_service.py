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


def ibm_sso_get_user_info(access_token: str):
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
