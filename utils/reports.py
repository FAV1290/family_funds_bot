from typing import Sequence
from datetime import timedelta as delta

from db.models import Income, Expense, Category


def compose_current_incomes_report(current_incomes: Sequence[Income], utc_offset: int = 0) -> str:
    if not current_incomes:
        return 'Приходы не найдены. Сочувствую!'
    incomes_sum = sum([income.amount for income in current_incomes])
    report = f'Общий бюджет текущего периода: {incomes_sum} руб.\n'
    report += 'Он формируется из следующих приходов:' if current_incomes else ''
    for income in current_incomes:
        created_at_str = (income.created_at + delta(hours=utc_offset)).strftime('%d.%m.%y, %H:%M')
        report += f'\n• ({created_at_str}): +{income.amount} руб.'
        report += f' ({income.description.capitalize()})' if income.description else ''
    return report


def compose_current_expenses_report(
    current_expenses: Sequence[Expense],
    current_incomes: Sequence[Income],
    utc_offset: int = 0,
) -> str:
    expenses_sum, expenses_list_str = 0, ''
    for expense in current_expenses:
        expenses_sum += expense.amount
        created_at_str = (expense.created_at + delta(hours=utc_offset)).strftime('%d.%m.%y, %H:%M')
        category = expense.category.name.capitalize() if expense.category_id else 'Без категории'
        expenses_list_str += f'• ({created_at_str}) ({category}): -{expense.amount} руб.'
        expenses_list_str += f' ({expense.description.capitalize()})' if expense.description else ''
        expenses_list_str += '\n'
    if not expenses_list_str:
        return 'Расходов не найдено. Везет же!'
    incomes_sum = sum([income.amount for income in current_incomes])
    report = f'Cписок ваших расходов в текущем периоде:\n{expenses_list_str}'
    report += f'\nВсего потрачено: {expenses_sum} руб.'
    if incomes_sum:
        report += f' из {incomes_sum} (остаток: {incomes_sum - expenses_sum})'
    return report


def compose_user_categories_report(
    current_incomes: Sequence[Income],
    current_expenses: Sequence[Expense],
    user_categories: Sequence[Category]
) -> str:
    if not user_categories:
        return 'Не вижу категорий расходов. Создадим?'
    limits_sum = 0
    incomes_sum = sum([income.amount for income in current_incomes])
    report = f'Общий бюджет на период: {incomes_sum} руб.\n\n' if incomes_sum else ''
    report += 'Вам доступны следующие категории расходов:'
    for category in user_categories:
        category_expenses_sum = sum(
            [expense.amount for expense in current_expenses if expense.category_id == category.id])
        report += f'\n • {category.name.capitalize()}'
        if category.limit:
            limits_sum += category.limit
            balance = category.limit - category_expenses_sum
            report += ' (Лимит: {}, расход: {}, остаток: {})'.format(
                category.limit, category_expenses_sum, balance)
        else:
            report += f' (Расход: {category_expenses_sum})'
    if incomes_sum:
        expenses_sum = sum([expense.amount for expense in current_expenses])
        report += '\n'.join([
            f'\nИсходя из лимитов, по итогам периода останется {incomes_sum - limits_sum} руб.',
            f'Текущий остаток: {incomes_sum - expenses_sum} из {incomes_sum} руб.',
        ])
    return report
