import os

import requests
from dotenv import load_dotenv

from ibm_sso.libs.error import AuthException
from ibm_sso.libs.logger import getLogger

load_dotenv()

W3ID_USER_INFO_URL = os.getenv('W3ID_USER_INFO_URL')
W3ID_CLIENT_ID = os.getenv('W3ID_CLIENT_ID')
W3ID_CLIENT_SECRET = os.getenv('W3ID_CLIENT_SECRET')
W3ID_ENDPOINT_INTROSPECT = os.getenv('W3ID_ENDPOINT_INTROSPECT')

logger = getLogger(__name__)


def sso_ibm_get_user_info(access_token: str):
    '''Get userinfo by access token'''

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.get(
        W3ID_USER_INFO_URL,
        headers=headers,
    )

    result = response.json()
    if (response.status_code == 200):
        return result
    else:
        logger.error(result['error'])
        raise AuthException(detail=result['error'])


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
    if (response.status_code == 200):
        if not result['active']:
            raise AuthException(detail=result['Invalid token'])
    else:
        logger.error(result)
        raise AuthException(detail=result['Invalid token!'])
