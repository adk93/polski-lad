# Standard library imports
import enum

# Third party imports
from flask import Blueprint, render_template, request, jsonify


# Local application imports
from kalkulator.main.forms import ContractOfEmploymentForm, ContractB2BProgressiveTax
from kalkulator.main.forms import ContractB2BFlatTax, ContractB2BRevenueTax

from kalkulator.main.calcEmployment import ContractOfEmployment2021, ContractOfEmployment2022
from kalkulator.main.calcB2B import B2Bscale2021, B2Bscale2022, \
    B2BFlat2021, B2BFlat2022, \
    B2BRevenueTax2021, B2BRevenueTax2022

from kalkulator.main.utils import DataValidator

class CalculatorTypes(enum.Enum):
    CONTRACT_OF_EMPLOYMENT = [ContractOfEmployment2021, ContractOfEmployment2022]
    B2B_SCALE =  [B2Bscale2021, B2Bscale2022]
    B2B_FLAT =  [B2BFlat2021, B2BFlat2022]
    B2B_REVENUE = [B2BRevenueTax2021, B2BRevenueTax2022]


main = Blueprint("main", __name__)

@main.route("/", methods=['GET', "POST"])
def index():
    employment_form = ContractOfEmploymentForm()
    scale_form = ContractB2BProgressiveTax()
    flat_form = ContractB2BFlatTax()
    revenue_form = ContractB2BRevenueTax()


    return render_template("index.html",
                           employment_form=employment_form,
                           scale_form=scale_form,
                           flat_form=flat_form,
                           revenue_form=revenue_form)



@main.route("/calculator", methods=['POST', 'GET'])
def calculator():

    if request.method == "POST":

        calcType = request.args.get('type')

        calc2021, calc2022 = CalculatorTypes[calcType].value

        data = request.get_json()

        print(data)

        validator = DataValidator(data)

        if validator.is_valid():

            result2021 = calc2021(**data)
            result2021.generate_table()

            result2022 = calc2022(**data)
            result2022.generate_table()

            summary = [result2021.get_summary(), result2022.get_summary()]

            results = {"2021": result2021.format_to_html(),
                       "2022": result2022.format_to_html(),
                       "summary": summary}

            return jsonify(results)

        else:
            return "invalid data!", 500




