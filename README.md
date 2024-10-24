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

1. Add `ibm-sso` to `requirements.txt`

    ```bash
    ibm-sso==0.3.0
    ```

    > For versions lower than `0.3.0`, the `token` is returned directly after successful authentication.
    > 
    > Starting from version `0.3.0`, you need to create your own `nonce` on the client side and then pass that `nonce` along with the `redirect_uri` to the server side. `code` and `state` are returned after successful authentication. You need to use the `code`, `state`, `nonce` and `redirect_uri` to obtain token information.

2. Install `ibm-sso` from `requirements.txt` file

    ```bash
    pipenv install -r requirements.txt
    ```

3. Set environment variables

    Refer to the [.env.template](./sample/.env.template) in the sample directory.

4. Import `ibm-sso` in startup file

    Refer to the [app.py](./sample/app.py) in the sample directory.

5. Protect your API

    If your API requires authentication to access, you can refer to [sample.py](./sample/api/v1/sample.py)

## Sample

There is a full sample in the `sample` directory that can be run directly. You can start from the sample to learn how to use `ibm-sso`.

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
    pipenv install -i https://test.pypi.org/simple/ ibm-sso
    ```

3. How to mark a version as yanked

    ```bash
    twine yank <package_name> --version <version> --reason "Reason this release was yanked: Yanked due to <reason>"
    ```
