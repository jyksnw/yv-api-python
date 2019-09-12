.PHONY: activate
activate:
	. ./venv/bin/activate

.PHONY: clean
clean:
	rm -rf dist/ build/ youversion.egg-info

.PHONY: build
build: activate clean
	python setup.py sdist


.PHONY: upload
upload: activate clean build
	twine upload dist/*

.PHONY: upload-test
upload-test: activate clean build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
