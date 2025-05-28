from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ibm_sso.authorize import authorize_router, get_current_user_for_middleware
from ibm_sso.vo.UserInfoVO import UserInfoMiddleWareVO
from starlette import status

from api.v1 import example_router

load_dotenv()

# Create FastAPI
app = FastAPI(
    title="ibm-sso example",
    description="ibm-sso example API Docs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redocs",
    debug=True,
)


@app.exception_handler(OAuthError)
async def oauth_error_exception_handler(request, exc: OAuthError):
    return JSONResponse(
        content={"detail": exc.error}, status_code=status.HTTP_401_UNAUTHORIZED
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception):
    return JSONResponse(
        content={"detail": exc.args}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_middleware_process_time_header(request: Request, call_next):

    user_info: UserInfoMiddleWareVO = await get_current_user_for_middleware(request)
    print(f"display_name={user_info.display_name}")

    response = await call_next(request)
    return response


app.include_router(authorize_router, prefix="/oauth2", tags=["Authorize API"])
app.include_router(example_router, prefix="/example", tags=["Example API"])
