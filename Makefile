.PHONY: install
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: test
test:
	python -m unittest discover . --pattern '*test.py'

.PHONY: coverage
coverage:
	coverage run -m unittest discover --pattern '*test.py'

.PHONY: coverage-report
coverage-report:
	coverage report -m

.PHONY: publish
publish:
	python setup.py sdist upload -r pypi

.PHONY: publish-test
publish-test:
	python setup.py sdist upload -r pypitest

.PHONY: register
register:
	python setup.py register -r pypi

.PHONY: register-test
register-test:
	python setup.py register -r pypitest

.PHONY: install-ve
install-ve:
	virtualenv --python `which python3` .ve
	.ve/bin/pip install -r requirements.txt
	.ve/bin/pip install -r requirements-dev.txt
	.ve/bin/pip install configparser

.PHONY: test-ve
test-ve:
	.ve/bin/python -m unittest discover . --pattern '*test.py'