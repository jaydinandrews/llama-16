test:
	python3 -m unittest discover -v

clean:
	find . | grep -E "__pycache__" | xargs rm -rf
	rm *.OUT
	rm *.SYM

deps:
	pip install coverage flake8

coverage:
	coverage erase
	coverage run -m unittest discover -v
	coverage report -m

lint:
	flake8 --exit-zero .

.PHONY: test clean deps coverage lint all
