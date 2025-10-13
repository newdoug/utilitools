"""Hashing utilities, functions, etc"""

from enum import auto
import hashlib
from typing import Callable, Dict

from Crypto.Hash import MD2, MD4

from mlc.utils.better_enum import BetterEnum


class HashType(BetterEnum):
    """Type of (unkeyed) hash algorithm"""

    MD2 = auto()
    # MD3??
    MD4 = auto()
    MD5 = auto()
    # MD6 = auto()
    SHA1 = auto()
    SHA224 = auto()
    SHA256 = auto()
    SHA384 = auto()
    SHA512 = auto()
    SHA3_224 = auto()
    SHA3_256 = auto()
    SHA3_384 = auto()
    SHA3_512 = auto()

    # TODO: implement
    # BLAKE2B = auto()
    # BLAKE2S = auto()

    # TODO: implement
    # SHAKE_128 = auto()
    # SHAKE_256 = auto()


# TODO: more: LSH, JH, HAVAL, HAS-160, GOST, FSB, ECOH, BLAKE-256, BLAKE-512,
# BLAKE2s, BLAKE2b, BLAKE2X, BLAKE3, RadioGatun, RIPEMD, RIPEMD-128,
# RIPDEMD-160, RIPEMD-256, RIPEMD-320, Skein, Snefru, Spectral Hash, Streebog,
# SWIFFT, Tiger, Whirlpool
# Some of these ^^ are commonly in openssl
# Will probably need other libraries or to implement them ourself


def md2(data: bytes) -> bytes:
    hasher = MD2.new()
    hasher.update(data)
    return hasher.digest()


def md4(data: bytes) -> bytes:
    hasher = MD4.new()
    hasher.update(data)
    return hasher.digest()


def _make_std_hashlib_hash_func(hash_class) -> Callable[[bytes], bytes]:
    # This is how most hashes (not *all*) from hashlib work
    # Certain blake ones are different as well as KDF-type ones
    return lambda data: hash_class(data).digest()


HASH_TYPE_TO_FUNC: Dict[HashType, Callable[[bytes], bytes]] = {
    HashType.MD2: md2,
    HashType.MD4: md4,
    HashType.MD5: _make_std_hashlib_hash_func(hashlib.md5),
    HashType.SHA1: _make_std_hashlib_hash_func(hashlib.sha1),
    HashType.SHA224: _make_std_hashlib_hash_func(hashlib.sha224),
    HashType.SHA256: _make_std_hashlib_hash_func(hashlib.sha256),
    HashType.SHA384: _make_std_hashlib_hash_func(hashlib.sha384),
    HashType.SHA512: _make_std_hashlib_hash_func(hashlib.sha512),
    HashType.SHA3_224: _make_std_hashlib_hash_func(hashlib.sha3_224),
    HashType.SHA3_256: _make_std_hashlib_hash_func(hashlib.sha3_256),
    HashType.SHA3_384: _make_std_hashlib_hash_func(hashlib.sha3_384),
    HashType.SHA3_512: _make_std_hashlib_hash_func(hashlib.sha3_512),
    # Can make other functions for whatever hash algorithm.
}


def hash_data(data: bytes, hash_type: HashType) -> bytes:
    """Hash `data` using `hash_type`"""
    return HASH_TYPE_TO_FUNC[hash_type](data)
