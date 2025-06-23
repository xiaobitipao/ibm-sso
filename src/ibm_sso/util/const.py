import os

ENV_AVATAR_PREFIX = os.getenv("W3ID_AVATAR_PREFIX")

# User Info avatar prefix
AVATAR_PREFIX = ENV_AVATAR_PREFIX or 'https://w3-ui-unified-profile-proxy.w3-ui.dal.app.cirrus.ibm.com/up-api-proxy/v3/image/'
