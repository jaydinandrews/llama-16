deps:
	pip install coverage flake8

coverage:
	coverage erase
	coverage run -m unittest discover -v
	coverage report -m

test:
	python3 -m unittest discover -v

lint:
	flake8 --exit-zero .

clean:
	rm -r **/__pycache__
	rm *.OUT
	rm *.SYM

.PHONY: deps all test clean
