import os
import sys
import json

def get_config_parser():
    if sys.version_info[0] == 3:
        from configparser import ConfigParser
        return ConfigParser
    else:
        import ConfigParser
        return ConfigParser.ConfigParser


ConfigParser = get_config_parser()
config = ConfigParser()
config.read('credentials.ini')

USERNAME = config.get('Credentials', 'USERNAME')
EXTENSION = config.get('Credentials', 'EXTENSION')
PASSWORD = config.get('Credentials', 'PASSWORD')
APP_KEY = config.get('Credentials', 'APP_KEY')
APP_SECRET = config.get('Credentials', 'APP_SECRET')
SERVER = config.get('Credentials', 'SERVER')
MOBILE = config.get('Credentials', 'MOBILE')