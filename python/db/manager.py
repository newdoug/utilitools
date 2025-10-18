from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import create_engine, Session, SQLModel


class DbManager:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(
            self.db_url, pool_pre_ping=True, pool_size=10, pool_recycle=3600
        )
        # Create tables
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        try:
            session = Session(self.engine)
            yield session
        except SQLAlchemyError:
            session.rollback()
        finally:
            session.commit()

    def queue_record_add(self, record):
        pass
        # TODO: in a separate thread/process, just pass a record to that thread/process and have it add to DB. Useful
        # for non-critical items like logs
