import sys, os
sys.path.insert(0, os.getcwd())

from src.backend.include.py3.ks_helper import KsHelper


def test_small_rand_bytes():
    inst = KsHelper()
    expected_length = 50
    assert len(inst.rand_bytes(expected_length)) == expected_length

def test_zero_rand_bytes():
    inst = KsHelper()
    expected_length = 0
    assert len(inst.rand_bytes(expected_length)) == expected_length

def test_large_rand_bytes():
    inst = KsHelper()
    expected_length = 2**20
    assert len(inst.rand_bytes(expected_length)) == expected_length

def test_negative_rand_bytes():
    inst = KsHelper()
    expected_length = 0
    assert len(inst.rand_bytes(-1)) == expected_length
