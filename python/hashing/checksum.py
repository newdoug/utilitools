"""Checksum functions, utilities, etc."""

from enum import auto
from typing import Callable, Dict

from mlc.utils.better_enum import BetterEnum


class ChecksumType(BetterEnum):
    """Type of checksum"""

    # TODO: implement these. zlib has some (adler32, crc32)
    ADLER32 = auto()
    BSD_UNIX = auto()
    DAMM = auto()
    FLETCHER4 = auto()
    FLETCHER8 = auto()
    FLETCHER16 = auto()
    FLETCHER32 = auto()
    IPV4_HEADER = auto()
    LUHN = auto()
    SUM8 = auto()
    SUM24 = auto()
    SUM32 = auto()
    SYSV_UNIX = auto()
    VERHOEFF = auto()
    XOR8 = auto()


CHECKSUM_TYPE_TO_FUNC: Dict[ChecksumType, Callable[[bytes], bytes]] = {
    ChecksumType.ADLER32: lambda data: data,  # TODO: actually implement
    ChecksumType.BSD_UNIX: lambda data: data,  # TODO: actually implement
}


def calc_checksum(data: bytes, checksum_type: ChecksumType) -> bytes:
    """Calculate checksum over `data` using `checksum_type`"""
    raise NotImplementedError()
