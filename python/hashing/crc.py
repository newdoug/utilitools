"""Cyclic redundancy check (CRC) functions, utilities, etc."""

# TODO: crc-mod? zlib might have some...

from dataclasses import dataclass
from enum import auto

from mlc.utils import BetterEnum


class CrcType(BetterEnum):
    """Type of CRC"""

    CKSUM = auto()
    CRC8 = auto()
    CRC16 = auto()
    CRC32 = auto()
    CRC64 = auto()


@dataclass
class CrcSettings:
    """Settings for a CRC calculation
    TODO: implement/finish
    E.g., polynomial value, initial value, specific algorithm (XMODE, CCITT,
    etc.)
    """

    polynomial: int | None = None
    initial_value: int | None = None
    alg_type: str | None = None


def calc_crc(data: bytes, crc_type: CrcType, crc_settings: CrcSettings) -> bytes:
    """Calculate a CRC over `data` of type `crc_type` with settings
    `crc_settings`
    """
    # TODO
