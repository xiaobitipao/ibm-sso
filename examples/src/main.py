import logging
import time

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

logger = logging.getLogger(__name__)

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

    if request.url.path in ["/oauth2/login", "/oauth2/token"]:
        return await call_next(request)

    # User info
    user_info: UserInfoMiddleWareVO = await get_current_user_for_middleware(request)
    logger.warning(f"Login user is: {user_info.email_address}")

    # Time measurement
    start_time = time.perf_counter()
    logger.warning("[API-TRACE] Start Request: %s %s", request.method, request.url.path)

    try:
        response = await call_next(request)
    finally:
        end_time = time.perf_counter()
        process_time = end_time - start_time
        logger.warning(
            "[API-TRACE] End Request:   %s %s - Duration: %.3f seconds",
            request.method,
            request.url.path,
            process_time,
        )
        response.headers["X-Process-Time"] = str(round(process_time, 3))

    return response


app.include_router(authorize_router, prefix="/oauth2", tags=["Authorize API"])
app.include_router(example_router, prefix="/example", tags=["Example API"])
