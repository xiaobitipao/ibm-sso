- [ibm-sso](#ibm-sso)
  - [Getting Started](#getting-started)
  - [Usage](#usage)
  - [Sample](#sample)
  - [Deploy project(memo for developer)](#deploy-projectmemo-for-developer)

# ibm-sso

When using `SSO Self-Service Provisioner` for single sign-on, `ibm-sso` can make your work easier.

> Currently only supports fastapi applications.

## Getting Started

```bash
pip install ibm-sso
```

## Usage

1. Add `ibm-sso` to `requirements.txt` file

    ```bash
    ibm-sso==0.0.1
    ```

2. Install `ibm-sso` from `requirements.txt` file

    ```bash
    pipenv install -r requirements.txt
    ```

3. Set environment variables

    Refer to the sample directory.

4. Import `ibm-sso` in startup file

    ```python
    from starlette.middleware.sessions import SessionMiddleware

    app = FastAPI()

    @app.exception_handler(OAuthError)
    async def oauth_error_exception_handler(request, exc: OAuthError):
        return JSONResponse(content={'detail': exc.error}, status_code=status.HTTP_401_UNAUTHORIZED)

    app.add_middleware(SessionMiddleware, secret_key='Change Me to Random Secret!')

    app.include_router(authorize_router, prefix='/oauth2', tags=['Authorize API'])
    ```

5. Now, your application has added SSO authentication functionality.

## Sample

There is a sample in the `sample` directory that can be run directly. You can start from the sample to learn how to use ibm-sso.

## Deploy project(memo for developer)

1. Deploy project

    ```bash
    # https://test.pypi.org/
    expect interactive_deploy_test.expect

    # https://pypi.org/
    # expect interactive_deploy.expect
    ```

2. Use `test.pypi.org`

    ```bash
    pipenv install  -i https://test.pypi.org/simple/ ibm-sso
    ```
