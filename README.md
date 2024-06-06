# ghidralyzer

**ghidralyzer** is a script that automates the process of creating a project, importing and analyzing a binary in Ghidra from the command line. If the provided target is a project file (`.gpr`), it will simply load the existing project.

## Features

- Cross-platform
- No external dependencies
- Supports creating a temporary project

## Usage

Specify the `GHIDRA_PATH`:
```python
GHIDRA_PATH = '/path/to/ghidra_11.0.3_PUBLIC' # CHANGE THIS
```

Create a project in the target path, import and analyze a binary:
```bash
python3 ghidralyzer.py /path/to/binary
```

Create a temporary project in the `TEMP_DIR`, import and analyze a binary:
```bash
python3 ghidralyzer.py /path/to/binary --temp
```

Load an existing project:
```bash
python3 ghidralyzer.py /path/to/project.gpr
```

## Special Thanks

- [liba2k](https://gist.github.com/liba2k/d522b4f20632c4581af728b286028f8f) - inspiration and code reference
