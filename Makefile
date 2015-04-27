.PHONY: test
test:
	python -m unittest discover . --pattern '*test.py'