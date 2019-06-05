.PHONY: install-tools
install-tools:
	sudo pip install virtualenv

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

.PHONY: install-ve-2
install-ve-2:
	virtualenv --python `which python2*` .ve2
	.ve2/bin/pip install -r requirements.txt
	.ve2/bin/pip install -r requirements-dev.txt

.PHONY: install-ve-3
install-ve-3:
	virtualenv --python `which python3` .ve3
	.ve3/bin/pip install -r requirements.txt
	.ve3/bin/pip install -r requirements-dev.txt
	.ve3/bin/pip install configparser

.PHONY: test-ve-2
test-ve-2:
	.ve2/bin/python -m unittest discover . --pattern '*test.py'

.PHONY: test-ve-3
test-ve-3:
	.ve3/bin/python -m unittest discover . --pattern '*test.py'

.PHONY: docker-login-3
docker-login-3:
	docker run -i -v $(shell pwd):/opt/sdk -t ringcentral-python-sdk-3 /bin/bash

.PHONY: docker-build-3
docker-build-3:
	docker build -t ringcentral-python-sdk-3 .

.PHONY: docker-login-2
docker-login-2:
	docker run -i -v $(shell pwd):/opt/sdk -t ringcentral-python-sdk-2 /bin/bash

.PHONY: docker-build-2
docker-build-2:
	docker build -t ringcentral-python-sdk-2 .