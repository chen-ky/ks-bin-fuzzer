import sys
from frontend.frontend import Frontend
from typing import List

import yaml

from backend.py3_generator import Python3Generator

ARGC_MIN = 2


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
    # code_gen = Python3Generator(ksy_source["meta"]["id"], ksy_source["seq"], ir.source) #TODO
    # code_gen.generate_code()
    return 0


if "__main__" == __name__:
    exit_code = main(sys.argv)
    exit(exit_code)
