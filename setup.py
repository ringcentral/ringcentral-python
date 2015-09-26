from distutils.core import setup

VERSION = __import__("ringcentral").VERSION

setup(
    name='ringcentral',
    packages=[
        'ringcentral',
        'ringcentral.core',
        'ringcentral.http',
        'ringcentral.mocks',
        'ringcentral.platform',
        'ringcentral.pubnub',
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
        'pubnub>=3.7.0',
        'requests>=2.7.0'
    ],
    classifiers=[]
)