import typing
from datetime import datetime

import pytest

from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase, Mapped, mapped_column


@pytest.fixture
def db_class() -> DeclarativeBase:
    class TestBase(DeclarativeBase):
        engine = create_engine('sqlite:///:memory:')
        session = scoped_session(sessionmaker(bind=engine))
    return TestBase


@pytest.fixture
def test_model(db_class) -> typing.Callable:
    def create_test_model(mixins=[]):
        class TestModel(db_class, *mixins):
            _next_instance_id = 0
            __tablename__ = 'test'
            id: Mapped[int] = mapped_column(primary_key=True)
            profile_id: Mapped[int] = mapped_column()
            created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

            def __init__(
                self,
                profile_id: int = 1,
                created_at: datetime = datetime.utcnow()
            ) -> None:
                self.id = TestModel._next_instance_id
                self.profile_id = profile_id
                self.created_at = created_at
                TestModel._next_instance_id += 1
        TestModel.metadata.create_all(bind=TestModel.engine)
        return TestModel

    return create_test_model
