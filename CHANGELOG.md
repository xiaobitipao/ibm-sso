# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2023-11-28

-   First commit

## [0.0.2] - 2023-12-06

-   Add avatar to UserInfoVO

## [0.0.3] - 2023-12-06

**Added**

-   Add avatar to UserInfoVO when the user authenticates.

## [0.0.4] - 2024-02-21

**Fixed**

-   Fixed mismatching_state and invalid_grant error.

## [0.0.5] - 2024-07-22

**Fixed**

-   Fixed pydantic.errors.PydanticUserError: Cannot create a Pydantic dataclass from UserInfoVO as it is already a Pydantic model.

## [0.1.0] - 2024-08-06

**Updated**

-   Replace token with code and state
-   Add `/token` and `/introspect` api.
