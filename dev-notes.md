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

## Run demos

Copy `.env.sample` to `.env`.

Edit `.env` to specify credentials

Run a demo file like this:

```
python demo_sms.py
```
