#!/usr/bin/python3
# -*- coding:utf-8 -*-

from api.v1 import sample_router
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.sessions import SessionMiddleware

from ibm_sso.authorize import authorize_router
from ibm_sso.libs.error import APIException

# Create FastAPI
app = FastAPI(
    title='ibm-sso sample',
    description='ibm-sso sample API Docs',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redocs',
    debug=True,
)


@app.exception_handler(Exception)
async def http_exception_handler(request, exc):
    if isinstance(exc, APIException):
        # If the type is APIException, it has been processed and can be returned directly.
        return JSONResponse(content={'detail': exc.detail}, status_code=exc.status_code)
    elif isinstance(exc, HTTPException):
        # If the type is HTTPException, because APIException inherits from HTTPException,
        # the exception information of HTTPException can be packaged into APIException and then returned.
        return JSONResponse(content={'detail': exc.detail}, status_code=exc.status_code)
    else:
        print(exc)
        if not app.debug:
            # If it is non-debugging mode, an error code is returned.
            return JSONResponse(content={'detail': 'Internal Server Error'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # If it is debugging mode, return detailed error information for developers to confirm
            raise exc

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
