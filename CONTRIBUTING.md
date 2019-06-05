# Publishing to PyPI

Read the article [How to submit a package to PyPI](http://peterdowns.com/posts/first-time-with-pypi.html).

Makefile scripts assume that you have `pypi` and `pypitest` sections in your `.pypirc` file:

```
[distutils]
index-servers =
    pypi
    pypitest

[pypi]
repository: https://pypi.python.org/pypi
username: xxx
password: xxx

[pypitest]
repository: https://test.pypi.org/legacy
username: xxx
password: xxx
```