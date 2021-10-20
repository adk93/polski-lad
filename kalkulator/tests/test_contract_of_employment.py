# Standard library imports


# Third party imports
import pytest

# Local application imports
from kalkulator.main.calcEmployment import ContractOfEmployment2021, ContractOfEmployment2022

TERMS_LIST = [
    (9000, 75996, 76464.24),
    (4000, 34880, 36259),
    (6785.44, 58459, 58447),
    (10000, 82907, 83245),
    (12000, 96730, 92271),
    (18000, 143532, 133639),
    (55000, 439901, 395598)
]

UNDER_26_TERMS_LIST = [
    {'grossSalary': 0, 'ppk': False, 'under26': True},
    {'grossSalary': 2500, 'ppk': True, 'under26': True},
    {'grossSalary': 11000, 'ppk': False, 'under26': True},
    {'grossSalary': 15000, 'ppk': True, 'under26': True},
    {'grossSalary': 50000, 'ppk': False, 'under26': True}
]


class TestContractOfEmployment2021:

    @pytest.mark.parametrize('grossSalary, net_salary2021, net_salary2022', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2021, net_salary2022):
        calc = ContractOfEmployment2021(**{'grossSalary': grossSalary, 'ppk': False, 'under26': False})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2021) / net_salary2021) < 0.015

    # Test Under26 Option
    @pytest.fixture(params=UNDER_26_TERMS_LIST)
    def calc_under_26(self, request):
        return ContractOfEmployment2021(**request.param)

    def test_under26_tax_paid(self, calc_under_26):
        assert calc_under_26.calculate_income_tax().sum() == 0


class TestContractOfEmployment2022:

    @pytest.mark.parametrize('grossSalary, net_salary2021, net_salary2022', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2021, net_salary2022):
        calc = ContractOfEmployment2022(**{'grossSalary': grossSalary, 'ppk': False, 'under26': False})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2022) / net_salary2022) < 0.015

    # Test Under26 Option
    @pytest.fixture(params=UNDER_26_TERMS_LIST)
    def calc_under_26(self, request):
        return ContractOfEmployment2022(**request.param)

    def test_under26_tax_paid(self, calc_under_26):
        assert calc_under_26.calculate_income_tax().sum() == 0

