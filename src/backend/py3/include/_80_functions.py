import zlib
import hashlib


def crc32(data: bytes) -> bytes:
    return int.to_bytes(zlib.crc32(data), 4)


def md5(data: bytes) -> bytes:
    return hashlib.md5(data, usedforsecurity=False).digest()


def sha1(data: bytes) -> bytes:
    return hashlib.sha1(data, usedforsecurity=False).digest()


def sha224(data: bytes) -> bytes:
    return hashlib.sha224(data).digest()


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha384(data: bytes) -> bytes:
    return hashlib.sha384(data).digest()


def sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def sha3_224(data: bytes) -> bytes:
    return hashlib.sha3_224(data).digest()


def sha3_256(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def sha3_384(data: bytes) -> bytes:
    return hashlib.sha3_384(data).digest()


def sha3_512(data: bytes) -> bytes:
    return hashlib.sha3_512(data).digest()
