import logging
from queue import Queue
import threading

from mlc.db.manager import DbManager
from mlc.db.model.logs import LogRecord


class DatabaseLogHandler(logging.Handler):
    def __init__(self, db_manager: DbManager):
        super().__init__()
        self.db_manager = db_manager
        self.stop = False
        self._log_db_thread = threading.Thread(target=self._log_db, daemon=True)
        self._db_records_queue = Queue()
        self._log_db_thread.start()

    def _log_db(self):
        while not self.stop or not self._db_records_queue.empty():
            record = self._db_records_queue.get()
            if not record:
                continue
            log = LogRecord(
                level=record.levelname,
                name=record.name,
                message=record.getMessage(),
                pathname=record.pathname,
                lineno=record.lineno,
                func=record.funcName,
                exception=self.formatException(record.exc_info) if record.exc_info else None,
            )
            with self.db_manager.get_session() as session:
                session.add(log)

    def emit(self, record: logging.LogRecord):
        # So, this is useful because we don't really want all users of the loggers to be blocked waiting for a
        # database transaction to finish. So, we push onto a queue and let another thread do it.
        self._db_records_queue.put(record)

    def close(self):
        self.stop = True
        # Edge case where the .get() above never times out or gets interrupted if there are no more records in the queue
        self._db_records_queue.put(None)
        self._log_db_thread.join()
