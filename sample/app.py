from api.v1 import sample_router
from authlib.integrations.base_client.errors import OAuthError
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.sessions import SessionMiddleware

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


# Save temporary code & state in session
app.add_middleware(SessionMiddleware, secret_key='Change Me to Random Secret!')

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
