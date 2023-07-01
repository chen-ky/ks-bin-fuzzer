from typing import List
from backend.py3_generator import Python3Generator
import yaml
import sys

ARGC_MIN = 2


def main(argv: List[str]) -> int:
    if len(argv) < ARGC_MIN:
        print("Please provide a .ksy file.", file=sys.stderr)
        return 1
    ksy_file_path = argv[1]
    ks_specification = None
    with open(ksy_file_path, "r") as f:
        ks_specification = yaml.safe_load(f)
    # print(ks_specification)
    code_gen = Python3Generator(ks_specification["meta"]["id"], ks_specification["seq"])
    code_gen.generate_code()


if "__main__" == __name__:
    exit_code = main(sys.argv)
    exit(exit_code)
