.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: test
test:
	python -m unittest discover . --pattern '*test.py'

.PHONY: publish
publish:
	python setup.py sdist upload -r pypi

.PHONY: publish-test
publish-test:
	python setup.py sdist upload -r https://testpypi.python.org/pypi

.PHONY: register
register:
	python setup.py register -r pypi

.PHONY: register-test
register-test:
	python setup.py register -r pypitest