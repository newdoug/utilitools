from datetime import datetime as dt, UTC


def get_utc_now() -> dt:
    return dt.now(UTC)


def get_utc_now_str() -> str:
    return get_utc_now().isoformat()
