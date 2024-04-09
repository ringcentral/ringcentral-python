## Install Python

The latest version at the time that I write this doc is 3.11.3

## Create virtual environment

Only do it if you have not done it before:

```
python -m venv venv
```

## Activate virtual environment

```
source venv/bin/activate
```

## Install dependencies

```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run unit tests

```
python -m unittest discover . --pattern '*test.py'
```
## Run unit tests with coverage report

```
coverage run -m unittest discover . --pattern '*test.py'

coverage report
```
Coverage Report Supported On
<ol>
    <li>Python 3.8 through 3.12, and 3.13.0a3 and up.</li>
    <li>PyPy3 versions 3.8 through 3.10</li>
</ol>





### Note

Subscription test requires necessary credentials in .env file. Your app will need "Websocket Subscriptions" permission.

## Run demos

Copy `.env.sample` to `.env`.

Edit `.env` to specify credentials

Run a demo file like this:

```
python3 ringcentral/demos/demo_fax.py
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
