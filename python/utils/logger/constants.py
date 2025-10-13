"""Common constants for logging"""

from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.absolute()
LOG_DIR = ROOT_DIR / "logs"
LOG_ARCHIVE_DIR = LOG_DIR / "archive"
SYS_LOG_PATH = "/dev/log"
