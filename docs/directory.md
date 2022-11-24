# 🦙📂 LLAMA-16 Project Structure 📂🦙
```
llama-16
├── Makefile
├── README.md
├── SPEC.txt
├── asm
├── emu
├── docs
├── prog
└── test
    ├── asm
    └── emu
        ├── bin
        └── src
```
### [asm](../asm)
The `asm` directory holds the source code for the LLAMA-16 Assembler. The assembler can be run from the `core.py` file within the `asm` directory. See the [LLAMA-16 Assembler](./assembler.md) document for usage of the assembler.

### [emu](../emu)
The `emu` directory holds the source code for the LLAMA-16 Emulator. The emulator can be run from the `core.py` file within the `emu` directory. This directory also somes some helper methods and functions used by the emulator. See the [LLAMA-16 Emulator])(./emulator.md) document for usage and available options for the emulator.

### [docs](.)
The `docs` directory holds the project documentation. This directory is the first stop new LLAMA-16 programmers should check out when starting out their exploration of this microarchitecture. The documents in this directory are seperated by use case and organzied like a project wiki. To get started with LLAMA-16 check out the project's [README](../README.md) or the main page of the [LLAMA-16 Wiki](./llama.md).

### [prog](../prog/)
The `prog` directory holds the source code of a few starter programs written for LLAMA-16. These files are intended to show of some of the features of the project as well as to serve as a practical reference for uses of some of the machine instructions. While checking out those programs, it may be helpful to refer to the [LLAMA-16 ISA](./isa.md) to look up syntax and usage of the instructions.

### [test](../test)
The `test` directory holds some source code of LLAMA programs that are intended for testing correctness and functionality of the assembler and emulator. While these programs may be handy for looking at syntax and usage of instructions, they should **not** be used as direct program logic references. The programs in the [test/asm](../test/asm) directory are strictly to be used to test the correctness of the assembler. If programs assembled from these files were run in the emulator they would run forever as there is no `hlt` instruction stopping computation. Furthermore, the logic is fairly non-sensical in that there is no logic to be found.

With that in mind, there are a few assemblable and runnable programs in the [test/emu](../test/emu) directory that are used to test functionality of the emulator. These programs can be used to explore and experiment with some of the functions of various instructions.

### [Makefile](../Makefile)
The `Makefile` is primarily used to clean up the project directory. While exploring and experimenting, it is easy to make mess of project directories. The Makefile can be used to clean of various Python caches, floating compiled binaries and symbol tables with the `make clean` command.

### [README](../README.md)
The `README` file is the first litle instroduction to LLAMA-16. The README is the first step into exploring the project.

### [SPEC](../SPEC.txt)
The `SPEC.txt` file is a basic outline of the LLAMA-16 Instruction Set Architecture. This nitty gritty text document acted (perhaps acts, present tense) as the blueprint for this project. It was the first file created when this project was started in February 2022. (Fun Fact: LLAMA-16 was orignally to be written in C! That didn't last long of course as who wants to make a text parser in C?)
If you'd like to see the evolution of the project, check out the git history of this file. A lot has changed since the inception of LLAMA-16.
