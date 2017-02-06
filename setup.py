from distutils.core import setup

VERSION = '0.7.5'

setup(
    name='ringcentral',
    packages=[
        'ringcentral',
        'ringcentral.http',
        'ringcentral.platform',
        'ringcentral.subscription',
        'ringcentral.test'
    ],
    version=VERSION,
    description='RingCentral Connect Platform Python SDK',
    author="Kirill Konshin @ RingCentral, Inc.",
    author_email="devsupport@ringcentral.com",
    url="https://github.com/ringcentral/ringcentral-python",
    download_url="https://github.com/ringcentral/ringcentral-python/tarball/%s" % VERSION,
    keywords=['sdk', 'ringcentral', 'connect', 'platform', 'api', 'python'],
    install_requires=[
        'observable>=0.3.1',
        'pubnub==4.*',
        'pycryptodome>=3.4.4',
        'requests>=2.7.0'
    ],
    classifiers=[]
)