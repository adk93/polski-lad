# Standard library imports
import bisect
from datetime import datetime

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from kalkulator.main.utils import Calculator, Rounder


class ContractOfEmployment(Calculator):
    """ Caltulates the costs of contract of employment"""

    def __init__(self, gross_salary, ppk, under_26):
        super().__init__(gross_salary)
        self.ppk = ppk
        self.under_26 = under_26

    def monthly_gross_salary(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.gross_salary

    @Rounder(decimals=2)
    def calculate_zus(self) -> np.ndarray:

        max_zus = self.DATA['MAX_ZUS_BASIS'] * self.DATA['EMPLOYEE_ZUS_RATE']
        monthly_zus = self.monthly_gross_salary() * self.DATA['EMPLOYEE_ZUS_RATE']

        monthly_cumulated_zus = monthly_zus.cumsum()
        monthly_cumulated_zus[monthly_cumulated_zus > max_zus] = max_zus

        monthly_cumulated_zus[1:] -= monthly_cumulated_zus[:-1].copy()

        return monthly_cumulated_zus

    def calculate_costs(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['COSTS']

    @Rounder()
    def calculate_income(self) -> np.ndarray:
        income = self.monthly_gross_salary() - self.calculate_zus()
        income[income < 0] = 0
        return income

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        return self.calculate_income() * self.DATA['HEALTH_INSURANCE_RATE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        return self.calculate_income() * self.DATA['HEALTH_INSURANCE_RATE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_net_salary(self) -> np.ndarray:
        return self.monthly_gross_salary() - self.calculate_zus() - self.calculate_nfz() - self.calculate_income_tax()

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        if self.under_26:
            return np.zeros(len(self.month_range))

        # Cumulated monthly income
        cumulated_income = self.calculate_income().cumsum() - self.middle_class_tax_relief().cumsum() - self.calculate_costs().cumsum()

        # Finds if at given month there is 17 or 32% of tax to pay
        tax_levels = np.array([self.find_tax_level(income) for income in cumulated_income])

        def get_tax(level, income):
            table = self.DATA['INCOME_TAX_TABLE']
            current_level = table[level-1]

            # calculate tax at given month
            tax_in_month = current_level.tax_rate * (income - current_level.min_income) + current_level.previous_level_tax

            return tax_in_month

        tax = np.array([get_tax(level, income) for level, income in zip(tax_levels, cumulated_income)])

        tax = tax - self.calculate_nfz_deductible().cumsum()

        paid_tax = []
        for x in np.nditer(tax):
            tax_to_pay = x - sum(paid_tax)

            if tax_to_pay > 0:
                paid_tax.append(tax_to_pay)
            else:
                paid_tax.append(0)

        return np.array(paid_tax)

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



    def generate_table(self) -> None:
        self.df = pd.DataFrame({
            "month": self.month_range,
            "gross_salary": self.monthly_gross_salary(),
            "costs": self.calculate_costs(),
            "income": self.calculate_income() - self.calculate_costs(),
            "nfz": self.calculate_nfz(),
            "income_tax": self.calculate_income_tax(),
            "net_salary": self.calculate_net_salary()
        })


class ContractOfEmployment2021(ContractOfEmployment):
    """Calculates costs of employment in 2020 before Nowy ład"""

    month_range: pd.DatetimeIndex = pd.date_range(datetime(2021, 1, 31), datetime(2021, 12, 31), freq="M")

    DATA: dict = {
        "EMPLOYEE_ZUS_RATE": 0.1371,
        "MAX_ZUS_BASIS": 157770,
        "COSTS": 250,
        "HEALTH_INSURANCE_RATE": 0.09,
        "HEALTH_INSURANCE_RATE_DEDUCTIBLE": 0.0775,
        "INCOME_TAX_TABLE": [Calculator.Tax_table(min_income=0,
                                                  max_income=3000,
                                                  tax_rate=0.00,
                                                  previous_level_tax=0),
                             Calculator.Tax_table(min_income=3000,
                                                  max_income=85528,
                                                  tax_rate=0.17,
                                                  previous_level_tax=0),
                             Calculator.Tax_table(min_income=85528,
                                                  max_income=np.inf,
                                                  tax_rate=0.32,
                                                  previous_level_tax=14539.76)]
    }

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary',3000),
                         kwargs.get('ppk', False),
                         kwargs.get('under26', False))


class ContractOfEmployment2022(ContractOfEmployment):
    """Calculates costs of employment in 2021 after Nowy ład"""

    month_range: pd.DatetimeIndex = pd.date_range(datetime(2022, 1, 31), datetime(2022, 12, 31), freq="M")

    DATA: dict = {
        "EMPLOYEE_ZUS_RATE": 0.1371,
        "MAX_ZUS_BASIS": 157770,
        "COSTS": 250,
        "HEALTH_INSURANCE_RATE": 0.09,
        "HEALTH_INSURANCE_RATE_DEDUCTIBLE": 0.0,
        "INCOME_TAX_TABLE": [Calculator.Tax_table(min_income=0, max_income=30000, tax_rate=0.00, previous_level_tax=0),
                             Calculator.Tax_table(min_income=30000, max_income=120000, tax_rate=0.17, previous_level_tax=0),
                             Calculator.Tax_table(min_income=120000, max_income=np.inf, tax_rate=0.32, previous_level_tax=20400)]
    }

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary',3000),
                         kwargs.get('ppk', False),
                         kwargs.get('under26', False))



