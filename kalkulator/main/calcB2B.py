# Standard library imports
import bisect
from collections import namedtuple
from datetime import datetime

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from kalkulator.main.utils import Calculator, Rounder


class B2B(Calculator):

    def __init__(self, gross_salary, zus):
        super().__init__(gross_salary)
        self.zus = zus

    def monthly_gross_salary(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.gross_salary

    @Rounder(decimals=2)
    def calculate_zus(self) -> np.ndarray:
        zus_data = self.DATA['SMALL_EMPLOYEE_ZUS'] if self.zus else self.DATA['EMPLOYEE_ZUS']
        return np.zeros(len(self.month_range)) + zus_data

    def calculate_costs(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.monthly_costs

    @Rounder()
    def calculate_income(self) -> np.ndarray:
        return self.monthly_gross_salary() - self.calculate_zus()

    @Rounder(decimals=2)
    def calculate_net_salary(self) -> np.ndarray:
        return self.monthly_gross_salary() - self.calculate_zus() - self.calculate_nfz() - self.calculate_income_tax() - self.calculate_costs()

    def middle_class_tax_relief(self) -> np.ndarray:
        """
        Obliczamy ulgę dla klasy średniej na podstawie algorytmu:
        https://www.e-pity.pl/polski-lad/ulga-dla-klasy-sredniej/

        Dla B2B podstawą są przychody minus koszty
        :return:

        Tablica numpy z kwotą odliczenia od podatku w każdym miesiącu osobno
        """

        base_range = np.zeros(len(self.month_range))

        relief_income_base = self.gross_salary - self.monthly_costs

        if self.month_range[0].year >= 2022:
            if relief_income_base > 11141:
                tax_relief = 0
            elif relief_income_base > 8549:
                tax_relief = (relief_income_base * (-0.0735) + 819.08) / 0.17
            elif relief_income_base >= 5701:
                tax_relief = (relief_income_base * 0.0668 - 380.5) / 0.17
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


class B2Bscale2021(B2B):
    month_range: pd.DatetimeIndex = pd.date_range(datetime(2021, 1, 31), datetime(2021, 12, 31), freq="M")

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.monthly_costs = float(kwargs.get('costs', 0))

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "HEALTH_INSURANCE": 381.81,
        "HEALTH_INSURANCE_DEDUCTIBLE": 328.78,
        "INCOME_TAX_TABLE": [Calculator.Tax_table(min_income=0, max_income=3091, tax_rate=0.00, previous_level_tax=0),
                             Calculator.Tax_table(min_income=3091, max_income=85528, tax_rate=0.17, previous_level_tax=0),
                             Calculator.Tax_table(min_income=85528, max_income=np.inf, tax_rate=0.32, previous_level_tax=14014.29)]
    }

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        cumulated_income = self.calculate_income().cumsum() - self.calculate_costs().cumsum()

        # Finds the level in tax table by income at given month
        tax_levels = np.array([self.find_tax_level(income) for income in cumulated_income])

        def get_tax(level, income):
            table = self.DATA['INCOME_TAX_TABLE']
            current_level = table[level - 1]

            # calculate tax at given month
            tax_in_month = current_level.tax_rate * (
                income - current_level.min_income) + current_level.previous_level_tax

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


class B2Bscale2022(B2B):

    month_range: pd.DatetimeIndex = pd.date_range(datetime(2022, 1, 31), datetime(2022, 12, 31), freq="M")

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.monthly_costs = float(kwargs.get('costs', 0))

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "MIN_INCOME": 3010,
        "HEALTH_INSURANCE_RATE": 0.09,
        "HEALTH_INSURANCE_RATE_DEDUCTIBLE": 0,
        "INCOME_TAX_TABLE": [Calculator.Tax_table(min_income=0, max_income=30000, tax_rate=0.00, previous_level_tax=0),
                             Calculator.Tax_table(min_income=30000, max_income=120000, tax_rate=0.17, previous_level_tax=0),
                             Calculator.Tax_table(min_income=120000, max_income=np.inf, tax_rate=0.32, previous_level_tax=15300)]
    }

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        monthly_income = self.calculate_income().copy()
        monthly_income[monthly_income < self.DATA['MIN_INCOME']] = self.DATA['MIN_INCOME']
        return monthly_income * self.DATA['HEALTH_INSURANCE_RATE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        monthly_income = self.calculate_income().copy()
        monthly_income[monthly_income < self.DATA['MIN_INCOME']] = self.DATA['MIN_INCOME']
        return monthly_income * self.DATA['HEALTH_INSURANCE_RATE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        cumulated_income = self.calculate_income().cumsum() - self.calculate_costs().cumsum() - self.middle_class_tax_relief().cumsum()

        # Finds the level in tax table by income at given month
        tax_levels = np.array([self.find_tax_level(income) for income in cumulated_income])

        def get_tax(level, income):
            table = self.DATA['INCOME_TAX_TABLE']
            current_level = table[level - 1]

            # calculate tax at given month
            tax_in_month = current_level.tax_rate * (
                income - current_level.min_income) + current_level.previous_level_tax

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



class B2BFlat2021(B2B):
    month_range: pd.DatetimeIndex = pd.date_range(datetime(2021, 1, 31), datetime(2021, 12, 31), freq="M")
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.monthly_costs = float(kwargs.get('costs', 0))
        self.ipbox = kwargs.get('ipbox', False)

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "HEALTH_INSURANCE": 381.81,
        "HEALTH_INSURANCE_DEDUCTIBLE": 328.78,
        "TAX_RATE": 0.19,
        "IPBOX_TAX_RATE": 0.05
    }

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        tax_rate = self.DATA['IPBOX_TAX_RATE'] if self.ipbox else self.DATA['TAX_RATE']
        return (self.calculate_income() - self.calculate_costs()) * tax_rate - self.calculate_nfz_deductible()



class B2BFlat2022(B2B):
    month_range: pd.DatetimeIndex = pd.date_range(datetime(2022, 1, 31), datetime(2022, 12, 31), freq="M")
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.monthly_costs = float(kwargs.get('costs', 0))
        self.ipbox = kwargs.get('ipbox', False)

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "MIN_INCOME": 3010,
        "HEALTH_INSURANCE_RATE": 0.049,
        "HEALTH_INSURANCE_RATE_DEDUCTIBLE": 0,
        "TAX_RATE": 0.19,
        "IPBOX_TAX_RATE": 0.05
    }

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        monthly_income = self.calculate_income().copy()
        monthly_income[monthly_income < self.DATA['MIN_INCOME']] = self.DATA['MIN_INCOME']
        return monthly_income * self.DATA['HEALTH_INSURANCE_RATE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        monthly_income = self.calculate_income().copy()
        monthly_income[monthly_income < self.DATA['MIN_INCOME']] = self.DATA['MIN_INCOME']
        return monthly_income * self.DATA['HEALTH_INSURANCE_RATE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        tax_rate = self.DATA['IPBOX_TAX_RATE'] if self.ipbox else self.DATA['TAX_RATE']
        return (self.calculate_income() - self.calculate_costs()) * tax_rate - self.calculate_nfz_deductible()


class B2BRevenueTax2021(B2B):
    month_range: pd.DatetimeIndex = pd.date_range(datetime(2021, 1, 31), datetime(2021, 12, 31), freq="M")
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.tax_rate = float(kwargs.get('taxRate', 0.15))
        self.monthly_costs = float(kwargs.get('costs', 0))

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "HEALTH_INSURANCE": 381.81,
        "HEALTH_INSURANCE_DEDUCTIBLE": 328.78,
    }

    @Rounder()
    def calculate_income(self) -> np.ndarray:
        return self.monthly_gross_salary() - self.calculate_zus()

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE']

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        return self.calculate_income() * self.tax_rate - self.calculate_nfz_deductible()


class B2BRevenueTax2022(B2B):
    month_range: pd.DatetimeIndex = pd.date_range(datetime(2022, 1, 31), datetime(2022, 12, 31), freq="M")

    NFZ_TABLE = namedtuple("nfz_table", ["min_salary", "max_salary", "health_insurance"])

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('grossSalary', 3000), kwargs.get('zus', False))
        self.tax_rate = float(kwargs.get('taxRate', 0.15))
        self.monthly_costs = float(kwargs.get('costs', 0))
        self.is_it = kwargs.get("is_it", False)
        self.is_medic = kwargs.get("is_medic", False)

    DATA: dict = {
        "EMPLOYEE_ZUS": 945.67,
        "SMALL_EMPLOYEE_ZUS": 265.78,
        "HEALTH_INSURANCE_TABLE": [NFZ_TABLE(min_salary=0, max_salary=60000, health_insurance=305.56),
                                   NFZ_TABLE(min_salary=60000, max_salary=300000, health_insurance=509.27),
                                   NFZ_TABLE(min_salary=300000, max_salary=np.inf, health_insurance=916.68)],
        "HEALTH_INSURANCE_DEDUCTIBLE": 0,
        "TAX_RATE_CHANGE" : {"IT": 0.12,
                             "MEDIC": 0.14}
    }

    @Rounder()
    def calculate_income(self) -> np.ndarray:
        return self.monthly_gross_salary() - self.calculate_zus()

    @Rounder(decimals=2)
    def calculate_nfz(self) -> np.ndarray:
        yearly_revenues = self.monthly_gross_salary().sum()

        nfz_level = bisect.bisect(list(map(lambda x: x.min_salary ,self.DATA['HEALTH_INSURANCE_TABLE'])),
                                  yearly_revenues)


        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE_TABLE'][nfz_level-1].health_insurance

    @Rounder(decimals=2)
    def calculate_nfz_deductible(self) -> np.ndarray:
        return np.zeros(len(self.month_range)) + self.DATA['HEALTH_INSURANCE_DEDUCTIBLE']

    @Rounder(decimals=2)
    def calculate_income_tax(self) -> np.ndarray:
        if self.is_it:
            tax_rate_2022 = self.DATA['TAX_RATE_CHANGE'].get("IT", 0.15)
        elif self.is_medic:
            tax_rate_2022 = self.DATA['TAX_RATE_CHANGE'].get("MEDIC", 0.17)
        else:
            tax_rate_2022 = self.tax_rate

        return self.calculate_income() * tax_rate_2022 - self.calculate_nfz_deductible()
