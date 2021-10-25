

function showForm(element) {

    var options = ["employment", "b2b-scale", "b2b-line", "b2b-revenue"];


    for (var i=0; i<options.length; i++){

        var option = options[i];
        var chosenSection = document.getElementById(option);

        if (option == element) {
            chosenSection.style.display = "block";
        } else {
            chosenSection.style.display = "none";
        };
    };


};

var grossSalary = document.getElementById("gross_salary");
var ppk = document.getElementById("ppk");
var under26 = document.getElementById("under_26");
var costs = document.getElementById("costs");
var zus = document.getElementById("zus");
var taxRate = document.getElementById("tax_rate");


function printResults(endpoint, server_data){
    $.ajax({
        type: "POST",
        url: "/calculator?" + $.param({type: endpoint}),
        data: JSON.stringify(server_data),
        contentType: "application/json",
        dataType: "json",
        statusCode: {
            500: function() {
                alert("błędnie wprowadzone dane");
            }
        },
        success: function(result) {

             var idTable2021 = document.getElementById("table-2021")
             var idTable2022 = document.getElementById("table-2022")
             var idSummary2021 = document.getElementById("summary-2021")
             var idSummary2022 = document.getElementById("summary-2022")
             var idSummaryCompare =document.getElementById("summary-compare")

            // clear if previously filled

            var allElements = [idTable2021, idTable2022, idSummary2021, idSummary2022, idSummaryCompare];

            allElements.forEach(e => e.innerHTML = '');

            // fill elements

            idTable2021.innerHTML = result["2021"]
            idTable2022.innerHTML = result["2022"]

            var summary2021, summary2022;

            [summary2021, summary2022] = result["summary"];

            idSummary2021.innerHTML = summary2021
            idSummary2022.innerHTML = summary2022
            idSummaryCompare.innerHTML = Math.abs(Math.floor((summary2022 / summary2021 - 1) * 100)) + "%";

            document.getElementById("greaterlower").innerHTML = (summary2022 > summary2021) ? "większe" : "mniejsze";

            animateResults();
        }
    });
};

function animateResults() {
    var results = document.querySelector(".calculator-results");
    results.removeAttribute("hidden");
    const reflow = results.offsetHeight;

    results.classList.add("show");

}

function calculate_contract_of_employment(a) {

    var f = a.parentNode.parentNode;

    var server_data = {
        "grossSalary": f.querySelector("#gross_salary").value,
        "under26": f.querySelector("#under_26").checked
    };

    console.log(server_data);

    printResults("CONTRACT_OF_EMPLOYMENT", server_data);
}

function calculate_b2b_scale(a) {

    var f = a.parentNode.parentNode;

    var server_data = {
        "grossSalary": f.querySelector("#gross_salary").value,
        "costs": f.querySelector("#costs").value,
        "zus": f.querySelector("#zus").checked
    };

    printResults("B2B_SCALE", server_data);
}

function calculate_b2b_line(a) {

    var f = a.parentNode.parentNode;

     var server_data = {
        "grossSalary": f.querySelector("#gross_salary").value,
        "costs": f.querySelector("#costs").value,
        "zus": f.querySelector("#zus").checked,
        "ipbox": f.querySelector("#ipbox").checked
    };

    printResults("B2B_FLAT", server_data);
};

function calculate_b2b_revenue(a) {

    var f = a.parentNode.parentNode;

    var server_data = {
        "grossSalary": f.querySelector("#gross_salary").value,
        "costs": f.querySelector("#costs").value,
        "taxRate": f.querySelector("#tax_rate").value,
        "zus": f.querySelector("#zus").checked,
        "is_it": f.querySelector("#is_it").checked,
        "is_medic": f.querySelector("#is_medic").checked
    };

    printResults("B2B_REVENUE", server_data);
};

var fieldsToValidate = document.querySelectorAll("input[name='gross_salary'], input[name='costs']");

for (var i=0; i<fieldsToValidate.length; i++) {
    fieldsToValidate[i].addEventListener("input", function() {
        if (this.value < 0 || this.value == '' || (isNaN(this.value))) {
            this.classList.add("invalid");
        } else {
            this.classList.remove("invalid");
        }
    })
}

function disableEnableMedicIT(el) {
    var elIds = document.querySelectorAll("#is_it, #is_medic");
    for (var i=0, c; c = elIds[i]; i++) {
        c.disabled =!(!el.checked || c === el);
    }
}
