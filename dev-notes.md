## Install uv

This repository uses [uv](https://docs.astral.sh/uv/) for Python interpreter management, dependency locking, command execution, and package building. Install it with:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install Python

The repository requests CPython 3.11 (the package's minimum supported version) in `.python-version`. Install it with uv — it is managed by uv and kept separate from your operating-system Python:

```
uv python install
```

## Synchronize dependencies

uv owns the project virtual environment (`.venv/`); manual activation is optional and not part of the canonical workflow. Install the locked dependencies with:

```
uv sync --locked
```

Locked synchronization installs exactly the versions recorded in `uv.lock`. If project metadata and the lockfile disagree, it fails instead of silently resolving new versions.

## Run unit tests

```
uv run --locked python -m unittest discover . --pattern '*test.py'
```

## Run unit tests with coverage report

```
uv run --locked coverage run -m unittest discover . --pattern '*test.py'

uv run --locked coverage report
```

## Generate API documentation

```
uv run --locked pdoc --output ./docs ./ringcentral
```

## Build distributions

Build the source distribution and wheel the way publish-style builds do, with uv-specific source overrides disabled:

```
uv build --no-sources
```

## Recreate the environment

To recreate the environment from scratch:

```
rm -rf .venv
uv sync --locked
```

## Update dependencies

Dependency updates are intentional, reviewable changes — ordinary setup and commands never modify the lockfile.

- After a declared constraint in `pyproject.toml` or a legacy requirements file changes, refresh the lockfile:

  ```
  uv lock
  ```

- To upgrade all eligible packages to their latest allowed versions:

  ```
  uv lock --upgrade
  ```

- To upgrade one named package:

  ```
  uv lock --upgrade-package <package>
  ```

Then synchronize and commit the updated `uv.lock`:

```
uv sync --locked
```

### Note

Unit tests, including the WebSocket subscription tests, use mocks. They are deterministic and require no RingCentral credentials.

## Run demos

Copy `.env.sample` to `.env`.

Edit `.env` to specify credentials. Live demos read credentials from this local environment file created from the existing sample.

Run a demo file like this:

```
uv run --locked python ringcentral/demos/demo_fax.py
```

The WebSocket subscription demo (`demo_subscription.py`) requires an application with the "WebSocket Subscriptions" permission.


## Release

Release is done by GitHub Action once a tag is pushed to the remote repo.

GitHub Action runs the following commands to release:

```
uv build --no-sources
uv run --locked twine upload dist/*
```

If you want to release it from your laptop, you need to have a ~/.pypirc file like this:

```
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-<your-token>
```

Then run the same release commands locally:

```
uv build --no-sources
uv run --locked twine upload dist/*
```
