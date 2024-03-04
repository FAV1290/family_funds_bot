def is_amount_str_valid(amount_str: str) -> bool:
    if not amount_str:
        return False
    validity_conditions = [amount_str.isdigit(), amount_str[0] != '0']
    return all(validity_conditions)


def is_category_name_valid(category_name: str, user_categories_names: list[str]) -> bool:
    lowered_categories_names_map = map(str.lower, user_categories_names)
    return all([
        category_name.strip(),
        0 < len(category_name) <= 64,
        category_name.strip().lower() not in lowered_categories_names_map,
    ])


def is_string_valid(string: str, length_limit: int) -> bool:
    return 0 < len(string) <= length_limit
