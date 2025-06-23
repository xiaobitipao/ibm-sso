- [ibm-sso](#ibm-sso)
  - [Getting Started](#getting-started)
  - [Usage](#usage)
  - [Examples](#examples)
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
    ibm-sso==0.3.2
    ```

    > For versions lower than `0.3.0`, the `token` is returned directly after successful authentication.
    > 
    > Starting from version `0.3.0`, you need to create your own `nonce` on the client side and then pass that `nonce` along with the `redirect_uri` to the server side. `code` and `state` are returned after successful authentication. You need to use the `code`, `state`, `nonce` and `redirect_uri` to obtain token information.

2. Set environment variables

    Refer to the [.env.template](./examples/.env.template) in the examples directory.

3. Import `ibm-sso` in startup file

    Refer to the [main.py](./examples/src/main.py) in the examples directory.

4. Protect your API

    If your API requires authentication to access, you can refer to [example.py](./examples/src/api/v1/example.py)

## Examples

There is a full example in the `examples` directory that can be run directly. You can start from the example to learn how to use `ibm-sso`.

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
    pip install -i https://test.pypi.org/simple/ ibm-sso
    ```

3. How to mark a version as yanked

    ```bash
    twine yank <package_name> --version <version> --reason "Reason this release was yanked: Yanked due to <reason>"
    ```
