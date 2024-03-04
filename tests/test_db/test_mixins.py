import random
from datetime import datetime

import pytest
from sqlalchemy import select
from freezegun import freeze_time
from sqlalchemy.exc import InvalidRequestError

from db.mixins import FetchByIDMixin, CreateMixin, SelfDeleteMixin, CurrentPeriodUserObjectsMixin


@pytest.mark.parametrize(
    'method_name',
    ['fetch_by_id', 'create', 'delete', 'fetch_current_period_objects'],
)
def test__models__dont_have_mixin_methods_in_initial_state(test_model, method_name: str) -> None:
    model = test_model()
    with pytest.raises(AttributeError):
        getattr(model, method_name)


def test__fetch_by_id_mixin__returns_none_for_non_existent_object(test_model) -> None:
    model = test_model(mixins=[FetchByIDMixin])
    assert model.fetch_by_id(target_id=0) is None


def test__fetch_by_id_mixin__finds_objects_by_their_ids(test_model) -> None:
    model = test_model(mixins=[FetchByIDMixin])
    model_objects = [model() for _ in range(10)]
    model.session.add_all(model_objects)
    model.session.commit()
    for object in model_objects:
        assert model.fetch_by_id(target_id=object.id) == object


def test__create_mixin__creates_objects(test_model) -> None:
    model = test_model(mixins=[CreateMixin])
    new_object = model.create()
    query = model.session.scalars(select(model)).all()
    assert len(query) == 1 and query[0] == new_object


def test__create_mixin__raises_type_error_for_unnecessary_kwargs_passed(test_model) -> None:
    model = test_model(mixins=[CreateMixin])
    with pytest.raises(TypeError):
        model.create(odd_attribute='Something')


def test__self_delete_mixin__deletes_objects(test_model):
    model = test_model(mixins=[CreateMixin, SelfDeleteMixin])
    new_object = model.create()
    assert len(model.session.scalars(select(model)).all()) == 1
    new_object.delete()
    assert len(model.session.scalars(select(model)).all()) == 0


def test__self_delete_mixin__raises_exception_for_not_persisted_instance_delete_attempt(
    test_model,
) -> None:
    model = test_model(mixins=[SelfDeleteMixin])
    new_object = model()
    with pytest.raises(InvalidRequestError):
        new_object.delete()


@freeze_time('2024-01-01')
def test__current_period_user_objects_mixin__finds_current_objects_among_others(test_model) -> None:
    model = test_model(mixins=[CurrentPeriodUserObjectsMixin])
    current_period_objects = [model() for _ in range(3)]
    other_objects = [model(created_at=datetime(
        year=2025, month=1, day=1)) for _ in range(50)]
    all_new_objects = current_period_objects + other_objects
    random.shuffle(all_new_objects)
    model.session.add_all(current_period_objects + other_objects)
    model.session.commit()
    assert set(model.fetch_current_period_objects(
        user_id=1, user_utc_offset=0)) == set(current_period_objects)


@freeze_time('2024-01-01')
def test__current_period_user_objects_mixin__returns_blank_list_in_absense_of_current_objects(
    test_model,
) -> None:
    model = test_model(mixins=[CurrentPeriodUserObjectsMixin])
    other_period_objects = [model(created_at=datetime(year=2025, month=1, day=1)) for _ in range(9)]
    model.session.add_all(other_period_objects)
    model.session.commit()
    assert model.fetch_current_period_objects(user_id=1, user_utc_offset=0) == []
