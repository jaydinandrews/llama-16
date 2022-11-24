clean:
	find . | grep -E "__pycache__" | xargs rm -rf
	find . | grep -E "*.OUT" | xargs rm -rf
	find . | grep -E "*.SYM" | xargs rm -rf

deps:
	pip install flake8

lint:
	flake8 --exit-zero .

.PHONY: clean deps lint all
