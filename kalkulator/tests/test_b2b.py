# Standard library imports


# Third party imports
import pytest

# Local application imports
from kalkulator.main.calcB2B import B2Bscale2021, B2Bscale2022
from kalkulator.main.calcB2B import B2BFlat2021, B2BFlat2022
from kalkulator.main.calcB2B import B2BRevenueTax2021, B2BRevenueTax2022

class TestB2BScale2021:

    TERMS_LIST = [
        (9000, 75877),
        (4000, 27805),
        (6785.44, 55547),
        (10000, 84037),
        (12000, 100357),
        (18000, 149317),
        (55000, 451237)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2021', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2021):
        calc = B2Bscale2021(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2021) / net_salary2021) < 0.015


class TestB2BScale2022:

    TERMS_LIST = [
        (9000, 76245),
        (4000, 29733),
        (6785.44, 55140),
        (10000, 84241),
        (12000, 94226),
        (18000, 136706),
        (55000, 398666)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2022', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2022):
        calc = B2Bscale2022(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2022) / net_salary2022) < 0.015


class TestB2BFlat2021:

    TERMS_LIST = [
        (9000, 75222),
        (4000, 26622),
        (6785.44, 53696),
        (10000, 84942),
        (12000, 104382),
        (18000, 162702),
        (55000, 522342)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2021', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2021):
        calc = B2BFlat2021(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2021) / net_salary2021) < 0.015


class TestB2BFlat2022:

    TERMS_LIST = [
        (9000, 71123),
        (4000, 25463),
        (6785.44, 50898),
        (10000, 80255),
        (12000, 98519),
        (18000, 153311),
        (55000, 491195)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2022', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2022):
        calc = B2BFlat2022(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2022) / net_salary2022) < 0.015


class TestB2BRevenueTax2021:

    TERMS_LIST = [
        (9000, 76585),
        (4000, 26785),
        (6785.44, 54528),
        (10000, 86545),
        (12000, 106465),
        (18000, 166225),
        (55000, 534745)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2021', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2021):
        calc = B2BRevenueTax2021(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250, 'taxRate':0.17})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2021) / net_salary2021) < 0.015


class TestB2BRevenueTax2022:

    TERMS_LIST = [
        (9000, 71110),
        (4000, 23754),
        (6785.44, 49053),
        (10000, 81070),
        (12000, 100990),
        (18000, 160750),
        (55000, 524381)
    ]

    @pytest.mark.parametrize('grossSalary, net_salary2022', TERMS_LIST)
    def test_net_salary(self, grossSalary, net_salary2022):
        calc = B2BRevenueTax2022(**{'grossSalary': grossSalary, 'zus': False, 'costs': 250, 'taxRate':0.17})
        calc.generate_table()
        calculated_net_salary = calc.df['net_salary'].sum()
        assert (abs(calculated_net_salary - net_salary2022) / net_salary2022) < 0.015

