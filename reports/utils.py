from djmoney.money import Money
from decimal import Decimal

from sales.models import Sale



def get_total_sales_revenue(sales: list[Sale], currency: str = None) -> Money:
    """
    Returns the total revenue made from a list of sales.

    :param sales: The list of sales to calculate revenue from.
    :param currency: The currency to return the revenue in. Defaults to the currency of the first sale.
    :return: The total revenue made from the sales.
    """
    if not sales:
        raise ValueError("No sales to calculate revenue from")
    
    currency = currency or sales[0].store.default_currency
    t = Money(Decimal(0), currency)
    for sale in sales:
        t += sale.revenue
    return t

