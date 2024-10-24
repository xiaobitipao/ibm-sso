from api.v1 import sample_router
from authlib.integrations.base_client.errors import OAuthError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status

from ibm_sso.authorize import authorize_router

# Create FastAPI
app = FastAPI(
    title='ibm-sso sample',
    description='ibm-sso sample API Docs',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redocs',
    debug=True,
)


@app.exception_handler(OAuthError)
async def oauth_error_exception_handler(request, exc: OAuthError):
    return JSONResponse(content={'detail': exc.error}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception):
    return JSONResponse(content={'detail': exc.args}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(authorize_router, prefix='/oauth2', tags=['Authorize API'])
app.include_router(sample_router, prefix='/sample', tags=['Sample API'])

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app='app:app',
        host='0.0.0.0',
        port=5000,
        reload=True,
        ssl_keyfile='./ssl_local/key.pem',
        ssl_certfile='./ssl_local/cert.pem',
    )
