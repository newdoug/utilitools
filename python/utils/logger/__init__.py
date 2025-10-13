"""Logging tools"""

from dataclasses import dataclass
import logging
import logging.handlers
from pathlib import Path
import os
import shutil
import sys
import tarfile

import asyncio

from .constants import LOG_ARCHIVE_DIR, LOG_DIR, SYS_LOG_PATH
from .dt import get_utc_now, get_utc_now_str


# The logger object that most are expected to use and import
LOG: logging.Logger = logging.getLogger(__name__)
DEFAULT_LOG_FORMAT_STR = (
    "%(name)s|%(asctime)s.%(msecs)03d|%(levelname)s|"
    "%(process)d:%(thread)d|"
    "%(filename)s:%(lineno)d|%(funcName)s: "
    "%(message)s"
)
# Applies to asctime. Then msecs in the format string gets milliseconds
LOG_RECORD_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
LOG_LEVEL_STR_TO_INT = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def path_dt() -> str:
    """Returns a base filename that has current time (UTC) in microseconds"""
    return f"{int(get_utc_now().timestamp() * 1000000)}"


def _generate_log_filename(logger_name: str) -> str:
    return f"{LOG_DIR}/{logger_name}_{path_dt()}.log"


def compress_logs(
    logger_name: str, log_dir: str, archive_dir: str, log_archive_chunk_size: int = 100
) -> None:
    if not os.path.isdir(log_dir):
        # Nothing to compress
        return
    os.makedirs(archive_dir, mode=0o750, exist_ok=True)

    chunk_num = 0

    def _compress_files(filenames: list[str]):
        arcname = f"{logger_name}_log_archive_{chunk_num}_{path_dt()}"
        os.makedirs(arcname, mode=0o750, exist_ok=True)
        for filename in filenames:
            if not filename:
                break
            dst_filename = os.path.join(arcname, os.path.basename(filename))
            os.rename(filename, dst_filename)

        compressed_logs_filename = os.path.join(archive_dir, f"{arcname}.tar.gz")
        with tarfile.open(compressed_logs_filename, mode="w:gz") as tar_file:
            tar_file.add(arcname)
        shutil.rmtree(arcname, ignore_errors=False)

    filenames = [None] * log_archive_chunk_size
    idx = 0
    for dir_entry in os.scandir(log_dir):
        if dir_entry.is_file() and dir_entry.name.lower().endswith(".log"):
            filenames[idx] = os.path.join(log_dir, dir_entry.name)
            idx += 1

        if idx >= log_archive_chunk_size:
            # Compress and reset counters
            _compress_files(filenames)
            idx = 0
            filenames = [None] * log_archive_chunk_size
            chunk_num += 1


def try_compress_logs(
    logger_name: str, log_dir: str, archive_dir: str, log_archive_chunk_size: int = 100
) -> None:
    try:
        compress_logs(logger_name, LOG_DIR, LOG_ARCHIVE_DIR)
    except (OSError, ValueError) as exc:
        eprint(f"Failed to compress log files in '{LOG_DIR}': {exc}")


def _create_trace_log_level(logger: logging.Logger, level_num: int = logging.DEBUG - 5) -> None:
    # Check if already done on this logger
    if hasattr(logging, "TRACE"):
        return
    logging.TRACE = level_num
    logging.addLevelName(level_num, "TRACE")
    LOG_LEVEL_STR_TO_INT["TRACE"] = level_num

    def _bound_log_method(self: logging.Logger, msg, *args, **kwargs):
        if self.isEnabledFor(level_num):
            # Otherwise, stacklevel=1 and the logged function name is this local function, which isn't helpful
            kwargs["stacklevel"] = kwargs.get("stacklevel", 1) + 1
            self._log(level_num, msg, args, **kwargs)

    logging.getLoggerClass().trace = _bound_log_method

    def _static_log_func(msg, *args, **kwargs):
        logging.log(level_num, msg, *args, **kwargs)

    logging.trace = _static_log_func


def set_up_logger(
    logger_name: str,
    logger: logging.Logger | None = None,
    compress_old_logs: bool = True,
    log_dir: str = LOG_DIR,
    archive_dir: str = LOG_ARCHIVE_DIR,
    use_stdout: bool = True,
    use_file: bool | str = True,
    use_syslog: bool = True,
    log_level: int | str = logging.INFO,
    log_format: str = DEFAULT_LOG_FORMAT_STR,
    additional_handlers: logging.Handler | list[logging.Handler] | None = None,
) -> logging.Logger:
    logger = logger or LOG
    logger.name = logger_name
    _create_trace_log_level(logger)
    if isinstance(log_level, str):
        log_level = LOG_LEVEL_STR_TO_INT[log_level.strip().upper()]
    logger.setLevel(log_level)
    formatter = logging.Formatter(log_format, LOG_RECORD_DATETIME_FORMAT)

    if compress_old_logs:
        try_compress_logs(logger_name, log_dir, archive_dir)

    if use_stdout:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    log_filename = None
    if use_file is True:
        log_filename = _generate_log_filename(logger_name)
    elif use_file:
        log_filename = use_file

    if log_filename:
        # Ensure directory where logs will be written to is created
        os.makedirs(log_dir, mode=0o750, exist_ok=True)
        os.makedirs(archive_dir, mode=0o750, exist_ok=True)

        handler = logging.FileHandler(log_filename)
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    if use_syslog:
        platform = sys.platform.lower()
        handler = None
        if platform.endswith("nux") or platform.endswith("nix"):
            if (
                hasattr(logging.handlers, "SysLogHandler")
                and os.path.exists(SYS_LOG_PATH)
                and os.access(SYS_LOG_PATH, os.R_OK)
            ):
                handler = logging.handlers.SysLogHandler(address=SYS_LOG_PATH)
        elif hasattr(logging.handlers, "NTEventLogHandler"):
            handler = logging.handlers.NTEventLogHandler(logger_name)

        if handler:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)
            logger.addHandler(handler)

    if additional_handlers:
        if not isinstance(additional_handlers, list):
            additional_handlers = [additional_handlers]
        for handler in additional_handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)
            logger.addHandler(handler)

    return logger


if __name__ == "__main__":

    def _main():
        set_up_logger(
            log_level=os.getenv("LOG_LEVEL", logging.DEBUG),
        )
        LOG.trace("Test TRACE message")
        LOG.debug("Test DEBUG message")
        LOG.info("Test INFO message")
        LOG.warning("Test WARNING message")
        LOG.error("Test ERROR message")
        LOG.critical("Test CRITICAL message")

    _main()
