import sys
from frontend.frontend import Frontend
from typing import List
from pathlib import Path
import shutil

import yaml

from backend.py3.code_generator import Python3CodeGenerator

ARGC_MIN = 2
DEFAULT_OUTPUT_DIR = Path("build")
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "output_fuzzer.py"


def main(argv: List[str]) -> int:
    if len(argv) < ARGC_MIN:
        print("Please provide a .ksy file.", file=sys.stderr)
        return 1
    ksy_file_path = argv[1]
    ksy_source = None
    with open(ksy_file_path, "r") as f:
        ksy_source = yaml.safe_load(f)
    frontend = Frontend(ksy_source)
    ir = frontend.generate_ir()

    # output = sys.stdout
    if DEFAULT_OUTPUT_DIR.exists():
        shutil.rmtree(DEFAULT_OUTPUT_DIR)
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = open(DEFAULT_OUTPUT_FILE, "w")
    code_gen = Python3CodeGenerator(ir, output)
    code_gen.generate_code()
    output.close()

    return 0


if "__main__" == __name__:
    exit_code = main(sys.argv)
    exit(exit_code)
