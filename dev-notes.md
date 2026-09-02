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
Coverage Report Supported On
<ol>
    <li>Python 3.8 through 3.12, and 3.13.0a3 and up.</li>
    <li>PyPy3 versions 3.8 through 3.10</li>
</ol>

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

Subscription test requires necessary credentials in .env file. Your app will need "Websocket Subscriptions" permission.

## Run demos

Copy `.env.sample` to `.env`.

Edit `.env` to specify credentials

Run a demo file like this:

```
uv run --locked python ringcentral/demos/demo_fax.py
```


## Release

Release will be done by GitHub Action once a tag is pushed to remote repo.

GitHub Action will run the following commands to release:

```
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
python3 -m build
twine upload dist/*
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
