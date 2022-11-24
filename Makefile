all:
	chmod +x ./asm/core.py
	chmod +x ./emu/core.py

build: asm emu

clean:
	find . | grep -E "__pycache__" | xargs rm -rf
	find . | grep -E "*.OUT" | xargs rm -rf
	find . | grep -E "*.SYM" | xargs rm -rf
	rm -rf build/
	rm -rf bin/

asm:
	pyinstaller --distpath ./bin --workpath ./build --clean -F --specpath ./build --name asm --paths asm/ asm/core.py

emu:
	pyinstaller --distpath ./bin --workpath ./build --clean -F --specpath ./build --name emu --paths emu/ emu/core.py

deps:
	pip install flake8 pyinstaller

lint:
	flake8 --exit-zero .

.PHONY: build clean deps lint asm emu all
