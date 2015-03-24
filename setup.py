from distutils.core import setup

VERSION = __import__("rcsdk").VERSION

setup(
    name='rcsdk',
    packages=[
        'rcsdk',
        'rcsdk.http',
        'rcsdk.platform',
        'rcsdk.subscription'
    ],
    version=VERSION,
    description='RingPlatform Python SDK',
    author="RingCentral, Inc.",
    author_email="devsupport@ringcentral.com",
    url="https://github.com/ringcentral/python-sdk",
    download_url="https://github.com/ringcentral/python-sdk/tarball/%s" % VERSION,
    keywords=['sdk', 'ringcentral', 'ringplatform'],
    install_requires=[
        'pubnub>=3.7.0',
    ],
    classifiers=[],
)