# Standard library imports
from datetime import datetime
from collections import namedtuple
from functools import wraps
import bisect

# Third party imports
import numpy as np
import pandas as pd

# Local application imports

class Rounder:
    def __init__(self, decimals: int = 0):
        self.decimals = decimals

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            arr = func(*args, **kwargs)
            return np.around(arr, self.decimals)
        return decorated


class Calculator:
    """Base of the calculator for calculating salary in 2022"""

    Tax_table = namedtuple("tax_table", ["min_income", "max_income", "tax_rate", "previous_level_tax"])

    def __init__(self, gross_salary):
        self.gross_salary = float(gross_salary)
        self.df: pd.DataFrame = None

    def find_tax_level(self, cumulated_income_at_month: float) -> int:
        return bisect.bisect(
            list(
                map(
                    lambda x: x.min_income,
                    self.DATA["INCOME_TAX_TABLE"])
            ),
            cumulated_income_at_month
        )


    def get_summary(self):
        return self.df['net_salary'].sum().round(2)

    def format_to_html(self):

        column_format_dict = {
            "month": "Miesiąc",
            "gross_salary": "Wynagrodzenie na umowie",
            "costs": "Koszty",
            "income": "Dochód",
            "nfz": "Składka zdrowotna",
            "income_tax": "Podatek dochodowy",
            "net_salary": "Wynagordzenie netto"
        }

        self.df.rename(column_format_dict, axis=1, inplace=True)

        classes = ["table", "summary-table", "table-condensed", "table-hover",
                   "table-borderless"]

        return self.df.round(0).to_html(index=False,
                                        classes=classes,
                                        justify="center",
                                        float_format="%.0f")

    def middle_class_tax_relief(self):

        base_range = np.zeros(len(self.month_range))

        if self.month_range[0].year >= 2022:
            if self.gross_salary > 11141:
                tax_relief = 0
            elif self.gross_salary > 8549:
                tax_relief = (self.gross_salary * (-0.0735) + 819.08) / 0.17
            elif self.gross_salary >= 5701:
                tax_relief = (self.gross_salary * 0.0668 - 380.5) / 0.17
            else:
                tax_relief = 0

            return base_range + tax_relief
        else:
            return base_range

class DataValidator:
    """
    server-side validation of ajax data
    """

    def __init__(self, data: dict):
        self.data = data

    def is_valid(self):
        validators = []

        for fieldName in ["grossSalary", "costs", "taxRate"]:
            field_data = float(self.data.get(fieldName, 1000))
            validator = (isinstance(field_data, float) or isinstance(field_data, int)) and field_data >= 0
            validators.append(validator)

        for fieldName in ['ppk', 'zus', 'under26', 'ipbox']:
            field_data = self.data.get(fieldName, False)
            validator = isinstance(field_data, bool)
            validators.append(validator)

        return np.all(validators)