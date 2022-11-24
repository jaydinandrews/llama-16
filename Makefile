PY = python3

test:
	$(PY) -m unittest discover -v

clean:
	rm -rf **/__pycache__


.PHONY: all test clean
