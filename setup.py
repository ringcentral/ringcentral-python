from distutils.core import setup

VERSION = __import__("rcsdk").VERSION

setup(
    name='rcsdk',
    packages=[
        'rcsdk',
        'rcsdk.core',
        'rcsdk.http',
        'rcsdk.http.mocks',
        'rcsdk.platform',
        'rcsdk.subscription',
        'rcsdk.test'
    ],
    version=VERSION,
    description='RingCentral Connect Platform Python SDK',
    author="RingCentral, Inc.",
    author_email="devsupport@ringcentral.com",
    url="https://github.com/ringcentral/python-sdk",
    download_url="https://github.com/ringcentral/python-sdk/tarball/%s" % VERSION,
    keywords=['sdk', 'ringcentral', 'connect', 'platform'],
    install_requires=[
        'pubnub>=3.7.0'
    ],
    classifiers=[]
)