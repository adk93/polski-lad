# Standard library imports

# Third party imports
from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, NumberRange

# Local application imports

class SalaryForm(FlaskForm):
    gross_salary = FloatField("Miesięczne wynagrodzenie brutto", validators=[NumberRange(min=0), DataRequired()])
    submit = SubmitField("Przelicz!")

class B2BForm(FlaskForm):
    costs = FloatField("Średnie miesięczny koszty uzyskania przychodów", validators=[NumberRange(min=0)], default=0)
    zus = BooleanField("Mały ZUS")

class ContractOfEmploymentForm(SalaryForm):
    under_26 = BooleanField("ulga dla osób do 26. roku życia")

class ContractB2BFlatTax(SalaryForm, B2BForm):
    ipbox = BooleanField("IP Box")

class ContractB2BProgressiveTax(SalaryForm, B2BForm):
    pass

class ContractB2BRevenueTax(SalaryForm, B2BForm):
    tax_rate = SelectField("Stopa podatku od przychodów", choices=[(0.17, '17%'),
                                                                   (0.15, '15%'),
                                                                   (0.125, '12.5%'),
                                                                   (0.10, '10%'),
                                                                   (0.085, '8,5%'),
                                                                   (0.055, '5.5%'),
                                                                   (0.03, '3%'),
                                                                   (0.02, '2%')])