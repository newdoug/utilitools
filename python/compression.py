#!/usr/bin/env python3
"""Data compression and decompression utilities"""

import bz2
from enum import auto
import gzip
import lzma
import os
import tarfile
import tempfile
from typing import Callable
import zlib

from mlc.utils.better_enum import BetterEnum

import zstd


def _to_tar_data(data: bytes, open_flags: str = "w") -> bytes:
    """tars up `data` and returns the tar contents.
    Supports both uncompressed and compressed based on `open_flags`
    """
    with (
        tempfile.NamedTemporaryFile() as raw_content_file,
        tempfile.NamedTemporaryFile() as file_tarred,
    ):
        raw_content_file.write(data)
        raw_content_file.flush()
        with tarfile.open(file_tarred.name, mode=open_flags) as tar_file:
            tar_file.add(raw_content_file.name)
            tar_filename = tar_file.name

        with open(tar_filename, "rb") as handle:
            return handle.read()


def _from_tar_data(data: bytes, open_flags: str = "r") -> bytes:
    """Interprets `data` as tar file contents and tries to untar them. Supports
    uncompressed and compressed formats of tar files (based on `open_flags`).
    """
    untarred_data = b""
    # This function is only a bit convoluted due to `tarfile` API pretty much
    # just doing this on files
    with (
        tempfile.NamedTemporaryFile() as raw_content_file,
        tempfile.TemporaryDirectory() as extract_dir,
    ):
        # Dump the binary tarfile contents to a temporary file
        raw_content_file.write(data)
        raw_content_file.flush()

        # Read the temporary file as a tar
        with tarfile.open(raw_content_file.name, mode=open_flags) as tar_file:
            # Extract everything to disk in temporary dir
            tar_file.extractall(path=extract_dir, filter="data")
            # If created with `_to_tar_data`, should just be 1 file, so
            # ordering doesn't matter
            for tinfo in tar_file.getmembers():
                # Should be an absolute path
                untarred_filename = os.path.join(extract_dir, tinfo.name)
                with open(untarred_filename, "rb") as handle:
                    untarred_data += handle.read()

    return untarred_data


_to_tar = _to_tar_data
_to_tar_gz = lambda data: _to_tar_data(data, "w:gz")
_to_tar_bz2 = lambda data: _to_tar_data(data, "w:bz2")
_to_tar_xz = lambda data: _to_tar_data(data, "w:xz")

_from_tar = _from_tar_data
_from_tar_gz = lambda data: _from_tar_data(data, "r:gz")
_from_tar_bz2 = lambda data: _from_tar_data(data, "r:bz2")
_from_tar_xz = lambda data: _from_tar_data(data, "r:xz")


class CompressionType(BetterEnum):
    """Type of compression algorithm"""

    GZIP = auto()
    # TODO
    # 7ZIP = auto()
    # RAR = auto()
    # ZIP = auto()
    # DEFLATE = auto()
    # LZ4 = auto()
    ZSTD = auto()
    # SNAPPY = auto()
    # BROTLI = auto()
    # Lempel-Ziv-Welch
    # LZW = auto()
    # LZ77 = auto()
    # LZ78 = auto()
    # PAQ = auto()
    # PPM = auto()
    # Run-length encoding
    # RLE = auto()
    # HUFFMAN = auto()
    # DELTA = auto()
    #
    # Burrows-Wheeler transform
    # BWT = auto()
    LZMA = auto()
    BZ2 = auto()
    ZLIB = auto()
    TAR = auto()
    TAR_GZ = auto()
    TAR_BZ2 = auto()
    TAR_XZ = auto()


# Example code (dead, but left for future reference) showing delta compression
# algorithm implementation. TODO
DELTA_EX_CODE = """
void delta_encode(unsigned char *buffer, int length)
{
    unsigned char last = 0;
    for (int i = 0; i < length; i++)
    {
        unsigned char current = buffer[i];
        buffer[i] = current - last;
        last = current;
    }
}

void delta_decode(unsigned char *buffer, int length)
{
    unsigned char last = 0;
    for (int i = 0; i < length; i++)
    {
        unsigned char delta = buffer[i];
        buffer[i] = delta + last;
        last = buffer[i];
    }
}
"""


def zstd_compress(data: bytes, level: int = 22) -> bytes:
    """ZSTD_compress doesn't have any keyword arguments, so the method used below causes an error because we pass level
    as a kwarg.
    """
    return zstd.ZSTD_compress(data, level)


# Compress function, decompress function, compression level kwarg name, max
# compression level value
TYPE_TO_FUNCS: dict[CompressionType, tuple[Callable, Callable, str, int]] = {
    CompressionType.GZIP: (gzip.compress, gzip.decompress, "compresslevel", 9),
    CompressionType.ZSTD: (zstd_compress, zstd.ZSTD_uncompress, "level", 22),
    CompressionType.LZMA: (
        lzma.compress,
        lzma.decompress,
        "preset",
        9 | lzma.PRESET_EXTREME,
    ),
    CompressionType.BZ2: (bz2.compress, bz2.decompress, "compresslevel", 9),
    CompressionType.ZLIB: (zlib.compress, zlib.decompress, "level", 9),
    CompressionType.TAR: (_to_tar, _from_tar, None, None),
    CompressionType.TAR_GZ: (_to_tar_gz, _from_tar_gz, None, None),
    CompressionType.TAR_BZ2: (_to_tar_bz2, _from_tar_bz2, None, None),
    CompressionType.TAR_XZ: (_to_tar_xz, _from_tar_xz, None, None),
}


def compress(data: bytes, comp_type: CompressionType, kwargs: dict | None = None) -> bytes:
    """Compress `data` using `comp_type` compression algorithm"""
    func_tup = TYPE_TO_FUNCS[comp_type]
    comp_func = func_tup[0]
    kwargs = kwargs or {}
    if func_tup[2] is not None and func_tup[3] is not None:
        if func_tup[2] not in kwargs:
            kwargs[func_tup[2]] = func_tup[3]
    return comp_func(data, **kwargs)


def decompress(data: bytes, comp_type: CompressionType, kwargs: dict | None = None) -> bytes:
    """Decompress `data` using `comp_type` compression algorithm"""
    func_tup = TYPE_TO_FUNCS[comp_type]
    kwargs = kwargs or {}
    return func_tup[1](data, **kwargs)
