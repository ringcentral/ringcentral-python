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

Release will be done by Github Action once a tag is pushed to remote repo
