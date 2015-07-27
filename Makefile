.PHONY: test
test:
	python -m unittest discover . --pattern '*test.py'

.PHONY: publish
publish:
	python setup.py sdist upload -r pypi

.PHONY: publish-test
publish-test:
	python setup.py sdist upload -r https://testpypi.python.org/pypi