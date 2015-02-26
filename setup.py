import os
from distutils.core import setup
from setuptools import find_packages

VERSION = __import__("lib").VERSION

CLASSIFIERS = []

install_requires = [
    'pycurl>=7.*',
    'pubnub>=3.*',
]

# taken from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('lib'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[12:] # Strip "lib/" or "lib\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(
    name="rcsdk",
    description="RingPlatform Python SDK",
    version=VERSION,
    author="RingCentral, Inc.",
    author_email="devsupport@ringcentral.com",
    url="https://github.com/ringcentral/python-sdk",
    download_url="https://github.com/ringcentral/python-sdk/archive/%s.zip" % VERSION,
    package_dir={'lib': 'lib'},
    packages=packages,
    package_data={'lib': data_files},
    include_package_data=True,
    install_requires=install_requires,
    classifiers=CLASSIFIERS,
)