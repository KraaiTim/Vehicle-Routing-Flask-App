/* TODO Change to work with something else than name */
function showReturn() {
    chboxs = document.getElementsByName("returnCheck");
    returns = document.getElementsByName("return");
    for (let i = 0; i < chboxs.length; i++) {
        // If the checkbox is checked, display the output text
        if (chboxs[i].checked) {
            returns[i].style.display = "none";
        } else {
            returns[i].style.display = "block";
        }
    }
};

//On change eventlistener to call Autocomplete API
var address_inputs = document.getElementsByName("depot_autcomplete");

address_inputs.forEach((element) => {
    element.addEventListener(
        'input',
        //Callback function
        (event) => {
            if (element.value.length >= 5) {
                (async () => {
                    autocomplete_body = await geocode_api(element.value, api_key, "autocomplete");
                    console.log(autocomplete_body["features"]);
                    autocomplete(element, autocomplete_body["features"]);
                })(element, api_key)
            }
        }
    )
});

//On Enter eventlistener to call Search API
address_inputs.forEach((element) => {
    element.addEventListener(
        'keypress',
        //Callback function
        (event) => {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action, if needed
                event.preventDefault();
                // Call Search API
                (async () => {
                    search_body = await geocode_api(element.value, api_key, "search");

                })(element, api_key)
            }
        })
});

//TODO Implement Throttle
const geocode_api = async (address, api_key, endpoint) => {
    let encoded_address = encodeURIComponent(address);
    let url = ""
    if (endpoint === "autocomplete") {
        url = `https://api.openrouteservice.org/geocode/autocomplete?api_key=${api_key}&text=${encoded_address}`
    }
    else {
        url = `https://api.openrouteservice.org/geocode/search?api_key=${api_key}&text=${encoded_address}`
    }
    // GET Request
    const response = await fetch(url);
    console.log(response.headers.get('x-ratelimit-limit'));
    console.log(response.headers.get('x-ratelimit-remaining'));
    
    const unixTimestamp = response.headers.get('x-ratelimit-reset')
    const milliseconds = unixTimestamp * 1000 
    const dateObject = new Date(milliseconds)
    console.log(dateObject)
    
    const data = await response.json();

    return data;
}

function addDepot() {
    depot = document.createElement("div");
    depot.setAttribute("class", "row");
    num_depot = (document.getElementsByName("depot_autcomplete").length / 2 + 1);
    depot.innerHTML =
        `<h5>Depot ${num_depot}</h5><button class="btn btn-danger"
        id="removeDepot" type="button" onclick="deleteDepot(this)">
        <i class="bi bi-trash"></i>
        Del
        </button>
        <div class="col-6 autocomplete">
        <label for="depot_autcomplete" class="form-label mb-0">Start address</label>
        <input type="text" class="form-control" id="depot_autcomplete"
            placeholder="Type address, autocomplete after 5 characters, search on Enter">
        <input id="start_lat_${num_depot}" name="start_lat_${num_depot}">
        <input id="start_long_${num_depot}" name="start_long_${num_depot}">
        <div class="form-check">
            <input class="form-check-input" type="checkbox" value="" id="flexCheckChecked" name="returnCheck"
                checked="checked" onclick="showReturn()">
            <label class="form-check-label" for="flexCheckChecked">
                Return to Start
            </label>
        </div>
        </div>
        <div class="col-6 autocomplete" name="return" style="display:none">
            <label for="depot_autcomplete" class="form-label mb-0">Return address</label>
            <input type="text" class="form-control" id="depot_autcomplete"
                placeholder="Type address, autocomplete after 5 characters, search on Enter">
            <input id="return_lat_${num_depot}" name="return_lat_${num_depot}">
            <input id="return_long_${num_depot}" name="return_long_${num_depot}">
        </div>`;

    document.getElementById('newdepot').appendChild(depot);
    /* Update depot inputs */
    address_inputs = document.getElementsByName("depot_autcomplete");
};

function deleteDepot(element) {
    element.closest(".row").remove();
    /* Update depot inputs */
    address_inputs = document.getElementsByName("depot_autcomplete");
}


/* Autocomplete 3WSchools https://www.w3schools.com/howto/howto_js_autocomplete.asp */
function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    var a, b, i, val = inp.value;
    /*close any already open lists of autocompleted values*/
    closeAllLists();
    if (!val) { return false;}
    currentFocus = -1;
    /*create a DIV element that will contain the items (values):*/
    a = document.createElement("DIV");
    a.setAttribute("id", inp.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    /*append the DIV element as a child of the autocomplete container:*/
    inp.parentNode.appendChild(a);
    /*for each item in the array...*/
    console.log("arr", arr);
    for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i]["properties"]["label"].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            /*create a DIV element for each matching element:*/
            b = document.createElement("DIV");
            /*make the matching letters bold:*/
            b.innerHTML = "<strong>" + arr[i]["properties"]["label"].substr(0, val.length) + "</strong>";
            b.innerHTML += arr[i]["properties"]["label"].substr(val.length);
            /*insert a input field that will hold the current array item's value:*/
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["label"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["geometry"]["coordinates"][0] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["geometry"]["coordinates"][1] + "'>";
            /* Add all information to dropdown */
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["street"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["housenumber"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["postalcode"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["locality"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["region"] + "'>";
            b.innerHTML += "<input type='hidden' value='" + arr[i]["properties"]["country"] + "'>";
            /*execute a function when someone clicks on the item value (DIV element):*/
            b.addEventListener("click", function(e) {
                /*insert the value for the autocomplete text field:*/
                inp.value = this.getElementsByTagName("input")[0].value;
                lat = inp.nextElementSibling
                lat.value = this.getElementsByTagName("input")[1].value;
                long = lat.nextElementSibling
                long.value = this.getElementsByTagName("input")[2].value;
                street = long.nextElementSibling
                street.value = this.getElementsByTagName("input")[3].value;
                number = street.nextElementSibling
                number.value = this.getElementsByTagName("input")[4].value;
                postcode = number.nextElementSibling
                postcode.value = this.getElementsByTagName("input")[5].value;
                city = postcode.nextElementSibling
                city.value = this.getElementsByTagName("input")[6].value;
                state = city.nextElementSibling
                state.value = this.getElementsByTagName("input")[7].value;
                country = state.nextElementSibling
                country.value = this.getElementsByTagName("input")[8].value;
                /*close the list of autocompleted values,
                (or any other open lists of autocompleted values:*/
                closeAllLists();
            });
            a.appendChild(b);
        }
    }

    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            //TODO add Search function here
            e.preventDefault();
            if (currentFocus > -1) {
            /*and simulate a click on the "active" item:*/
            if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
        }
    }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}