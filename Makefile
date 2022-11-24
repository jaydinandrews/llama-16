test:
	python3 -m unittest -v

clean:
	find . | grep -E "__pycache__" | xargs rm -rf
	find . | grep -E "*.OUT" | xargs rm -rf
	find . | grep -E "*.SYM" | xargs rm -rf

deps:
	pip install coverage flake8

coverage:
	coverage erase
	coverage run -m unittest discover -v
	coverage report -m

lint:
	flake8 --exit-zero .

.PHONY: test clean deps coverage lint all
