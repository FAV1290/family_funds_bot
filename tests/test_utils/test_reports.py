from unittest.mock import PropertyMock, patch

import pytest
from freezegun import freeze_time

from utils.reports import (
    compose_current_incomes_report,
    compose_current_expenses_report,
    compose_user_categories_report,
)
from db.models import Income, Expense, Category


def test__compose_current_incomes_report__empty_incomes_list_case() -> None:
    assert compose_current_incomes_report([]) == 'Приходы не найдены. Сочувствую!'


@freeze_time('2024-01-01')
def test__compose_current_incomes_report__filled_incomes_list_case() -> None:
    incomes = [
        Income(profile_id=1, amount=100, description='one'),
        Income(profile_id=1, amount=200, description='two'),
        Income(profile_id=1, amount=300),
    ]
    expected_result = ''.join([
        'Общий бюджет текущего периода: 600 руб.\n',
        'Он формируется из следующих приходов:',
        '\n• (01.01.24, 00:00): +100 руб. (One)',
        '\n• (01.01.24, 00:00): +200 руб. (Two)',
        '\n• (01.01.24, 00:00): +300 руб.',
    ])
    assert compose_current_incomes_report(incomes) == expected_result


@freeze_time('2024-01-01')
def test__compose_current_incomes_report__shifts_time_according_to_utc_offset() -> None:
    incomes = [Income(profile_id=1, amount=100, description='one')]
    expected_result = ''.join([
        'Общий бюджет текущего периода: 100 руб.\n',
        'Он формируется из следующих приходов:',
        '\n• (01.01.24, 03:00): +100 руб. (One)',
    ])
    assert compose_current_incomes_report(incomes, utc_offset=3) == expected_result


@pytest.mark.parametrize('incomes', [[], [Income(profile_id=1, amount=100, description='one')]])
def test__compose_current_expenses_report__empty_expenses_list_cases(incomes) -> None:
    assert compose_current_expenses_report([], incomes) == 'Расходов не найдено. Везет же!'


@patch('db.models.Expense.category', new_callable=PropertyMock)
@freeze_time('2024-01-01')
def test__compose_current_expenses_report__filled_lists_case(expense_category_mock) -> None:
    expense_category_mock.return_value = Category(profile_id=1, name='test')
    expenses = [
        Expense(profile_id=1, amount=100, description='one'),
        Expense(profile_id=1, amount=300, category_id=1),
    ]
    incomes = [Income(profile_id=1, amount=1000)]
    expected_result = ''.join([
        'Cписок ваших расходов в текущем периоде:\n',
        '• (01.01.24, 00:00) (Без категории): -100 руб. (One)\n',
        '• (01.01.24, 00:00) (Test): -300 руб.\n',
        '\nВсего потрачено: 400 руб. из 1000 (остаток: 600)'
    ])
    assert compose_current_expenses_report(expenses, incomes) == expected_result


@freeze_time('2024-01-01')
def test__compose_current_expenses_report__shifts_time_according_to_utc_offset() -> None:
    expenses = [Expense(profile_id=1, amount=100)]
    expected_result = ''.join([
        'Cписок ваших расходов в текущем периоде:\n',
        '• (01.01.24, 03:00) (Без категории): -100 руб.\n',
        '\nВсего потрачено: 100 руб.'
    ])
    assert compose_current_expenses_report(expenses, [], utc_offset=3) == expected_result


def test__compose_user_categories_report__empty_categories_list_case() -> None:
    assert compose_user_categories_report([], [], []) == 'Не вижу категорий расходов. Создадим?'


def test__compose_user_categories_report__filled_categories_list_only_case() -> None:
    assert compose_user_categories_report([], [], [Category(profile_id=1, name='pc')]) == ''.join([
        'Вам доступны следующие категории расходов:',
        '\n • Pc (Расход: 0)',
    ])


@patch('db.models.Category.id', new_callable=PropertyMock)
def test__compose_user_categories_report__filled_lists_case(expense_category_mock) -> None:
    expense_category_mock.return_value = 1
    incomes = [Income(profile_id=1, amount=1000)]
    expenses = [Expense(profile_id=1, amount=100, category_id=1)]
    categories = [
        Category(profile_id=1, name='food', limit=500),
        Category(profile_id=1, name='rent'),
    ]
    expected_result = ''.join([
        'Общий бюджет на период: 1000 руб.\n\n',
        'Вам доступны следующие категории расходов:',
        '\n • Food (Лимит: 500, расход: 100, остаток: 400)',
        '\n • Rent (Расход: 100)',
        '\nИсходя из лимитов, по итогам периода останется 500 руб.',
        '\nТекущий остаток: 900 из 1000 руб.',
    ])
    assert compose_user_categories_report(incomes, expenses, categories) == expected_result
