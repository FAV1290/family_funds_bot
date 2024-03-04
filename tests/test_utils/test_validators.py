import pytest

from utils.validators import is_amount_str_valid, is_string_valid, is_category_name_valid


@pytest.mark.parametrize(
    'raw_amount',
    [
        pytest.param('', id='blank string'),
        pytest.param(' ', id='lonely space symbol'),
        pytest.param('b', id='lonely non-digit symbol'),
        pytest.param('0', id='lonely zero digit'),
        pytest.param('      ', id='spaces sequence'),
        pytest.param('00000000000', id='zeroes sequence'),
        pytest.param('012', id='leading by zero digit sequence'),
        pytest.param('0ABCDEFG', id='leading by zero non-digit sequence'),
        pytest.param('ABCDEFG', id='non-digit sequence'),
        pytest.param('-100', id='negative amount'),
        pytest.param('+100', id='positive amount with plus symbol'),
        pytest.param('\u0001', id='non-digit unicode symbol with digit code'),
        pytest.param('123 456', id='digit sequence with space'),
        pytest.param('234 567 890', id='digit sequence with spaces'),
        pytest.param(' 123', id='digit sequence with leading space'),
        pytest.param('123 ', id='digit sequence with trailing space'),
        pytest.param('123.456.789', id='digit sequence with dot delimiters'),
        pytest.param('123,456,789', id='digit sequence with comma delimiters'),
    ],
)
def test__is_amount_str_valid__false_cases(raw_amount: str) -> None:
    assert not is_amount_str_valid(raw_amount)


@pytest.mark.parametrize(
    'raw_amount',
    [
        pytest.param('\u0031', id='digit unicode symbol with digit code'),
        pytest.param('1', id='lonely non-zero digit'),
        pytest.param('12345', id='valid input without zeroes'),
        pytest.param('10000', id='valid input with zeroes'),
    ],
)
def test__is_amount_str_valid__true_cases(raw_amount: str) -> None:
    assert is_amount_str_valid(raw_amount)


@pytest.mark.parametrize(
    'string, length_limit, expected_result',
    [
        pytest.param('', 10, False, id='blank string'),
        pytest.param(' ', 10, True, id='blank string with space'),
        pytest.param('smth short', 15, True, id='text len does not overdraw limit'),
        pytest.param('something long enough', 15, False, id='text len overdraws limit'),
        pytest.param('something', 9, True, id='equal to limit text len'),
        pytest.param('', 0, False, id='zero limit and blank string'),
        pytest.param('test', 0, False, id='zero limit and non-blank string'),
    ],
)
def test__is_string_valid__validates_strings_in_a_proper_way(
    string: str,
    length_limit: int,
    expected_result: bool
) -> None:
    assert is_string_valid(string, length_limit) == expected_result


def test__is_string_valid__wont_raise_exception_on_negative_limit() -> None:
    assert not is_string_valid('test', -1)


@pytest.mark.parametrize(
    'category_name',
    [
        pytest.param('existing name', id='existing category name - exact match'),
        pytest.param('ExIsTiNg NaMe', id='existing category name - case insensitive match'),
        pytest.param('  existing name  ', id='existing category name - stripped match'),
        pytest.param('a'*65, id='too long category name'),
        pytest.param('', id='blank string'),
        pytest.param(' ', id='space'),

    ],
)
def test__is_category_name_valid__false_cases(category_name: str) -> None:
    assert not is_category_name_valid(category_name, ['existing name'])


def test__is_category_name_valid__true_case() -> None:
    assert is_category_name_valid('non-existent category name', ['existing category name'])


def test__is_category_name_valid__works_with_empty_categories_names_list() -> None:
    assert is_category_name_valid('test', [])
