from setuptools import setup, find_packages

VERSION = '0.9.2'

setup(
    name='ringcentral',
    packages=find_packages(exclude=[]),
    version=VERSION,
    description='RingCentral Python SDK',
    author='Kirill Konshin',
    url='https://github.com/ringcentral/ringcentral-python',
    download_url='https://github.com/ringcentral/ringcentral-python/tarball/%s' % VERSION,
    keywords=['sdk', 'ringcentral', 'connect', 'platform', 'api', 'python'],
    install_requires=[i.strip() for i in open('requirements.txt').readlines()],
    classifiers=[]
)
