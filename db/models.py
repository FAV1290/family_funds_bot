import uuid
from typing import Annotated
from datetime import datetime, timedelta

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, BigInteger, UUID, ForeignKey

from db import FFBase
from db.mixins import FetchByIDMixin, CreateMixin, SelfDeleteMixin, CurrentPeriodUserObjectsMixin

UUID_BASED_ID = Annotated[uuid.UUID, mapped_column(UUID, primary_key=True)]
CREATED_AT = Annotated[datetime, mapped_column(DateTime, default=datetime.utcnow)]
UPDATED_AT = Annotated[
    datetime,
    mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
]


class Profile(FFBase, FetchByIDMixin, CreateMixin):
    __tablename__ = 'profiles'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    utc_offset: Mapped[int] = mapped_column(default=0)
    categories: Mapped[list['Category']] = relationship(back_populates='profile')
    expenses: Mapped[list['Expense']] = relationship(back_populates='profile')
    incomes: Mapped[list['Income']] = relationship(back_populates='profile')
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]

    def __init__(self, chat_id: int, utc_offset: int = 0) -> None:
        self.id = chat_id
        self.utc_offset = utc_offset

    @classmethod
    def fetch_by_id_or_create(cls, chat_id: int, utc_offset: int = 0) -> 'Profile':
        return cls.fetch_by_id(chat_id) or cls.create(chat_id=chat_id, utc_offset=utc_offset)

    def set_utc_offset(self, new_utc_offset: int) -> None:
        self.utc_offset = new_utc_offset
        self.session.commit()


class Category(FFBase, FetchByIDMixin, CreateMixin):
    __tablename__ = 'categories'
    id: Mapped[UUID_BASED_ID]
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    profile: Mapped['Profile'] = relationship(back_populates='categories')
    name: Mapped[str] = mapped_column(String(64))
    limit: Mapped[int | None] = mapped_column(default=None)
    expenses: Mapped[list['Expense']] = relationship(back_populates='category')
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]

    def __init__(self, profile_id: int, name: str, limit: int | None = None) -> None:
        self.id = uuid.uuid4()
        self.profile_id = profile_id
        self.name = name
        self.limit = limit

    def update_limit(self, new_limit: int) -> None:
        self.limit = new_limit
        self.session.commit()


class Expense(FFBase, CreateMixin, SelfDeleteMixin, CurrentPeriodUserObjectsMixin):
    __tablename__ = 'expenses'
    id: Mapped[UUID_BASED_ID]
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    profile: Mapped['Profile'] = relationship(back_populates='expenses')
    amount: Mapped[int] = mapped_column()
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('categories.id', ondelete='SET NULL'))
    category: Mapped['Category'] = relationship(back_populates='expenses')
    description: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]

    def __init__(
        self,
        profile_id: int,
        amount: int,
        category_id: UUID | None = None,
        description: str | None = None,
    ) -> None:
        self.id = uuid.uuid4()
        self.profile_id = profile_id
        self.amount = amount
        self.category_id = category_id
        self.description = description
        self.created_at = datetime.utcnow()

    def __str__(self) -> str:
        utc_offset = self.profile.utc_offset if self.profile else 0
        expense_str_map = {
            'добавлен': (self.created_at + timedelta(
                hours=utc_offset)).strftime('%d-%m-%Y %H:%M:%S'),
            'сумма': str(self.amount),
            'категория': self.category.name.capitalize() if self.category_id else '—',
            'описание': self.description or '—',
        }
        return '• ' + '\n• '.join(
            [f'{key.capitalize()}: {value}' for key, value in expense_str_map.items()])


class Income(FFBase, CreateMixin, CurrentPeriodUserObjectsMixin):
    __tablename__ = 'incomes'
    id: Mapped[UUID_BASED_ID]
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id', ondelete='CASCADE'))
    profile: Mapped['Profile'] = relationship(back_populates='incomes')
    amount: Mapped[int] = mapped_column()
    description: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[CREATED_AT]
    updated_at: Mapped[UPDATED_AT]

    def __init__(self, profile_id: int, amount: int, description: str | None = None) -> None:
        self.id = uuid.uuid4()
        self.profile_id = profile_id
        self.amount = amount
        self.description = description
        self.created_at = datetime.utcnow()


def create_tables() -> None:
    FFBase.metadata.create_all(bind=FFBase.engine)
