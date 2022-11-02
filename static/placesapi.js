
    //Get Google Places API from Flask session and create script tag with API key
    var googleplaces_api_key = "{{ session['googleplaces_api_key'] }}";
    var stag = document.createElement('script');
    stag.src = ("https://maps.googleapis.com/maps/api/js?key=" + googleplaces_api_key + "&libraries=places&callback=initAutocomplete")
    stag.defer = true;
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.insertBefore(stag, firstScriptTag.nextSibling);

    //Google Places Autocomplete API call
    let autocomplete;
    function initAutocomplete() {
        autocomplete = new google.maps.places.Autocomplete(
            document.getElementById('depot'),
            {
                componentRestrictions: { country: ['BE', 'NL'] },
                fields: ['geometry']
            });
        autocomplete.addListener('place_changed', onPlaceChanged);
    }
    function onPlaceChanged() {
        var place = autocomplete.getPlace();

        if (!place.geometry) {
            //User did not select a prediction; reset the input field
            document.getElementById('autocomplete').placeholder =
                'Enter a place';
        } else {
            //Display details about the valid place
            let lat = place.geometry.location.lat(),
                lng = place.geometry.location.lng();
            document.getElementById('depot_lat').value = lat
            document.getElementById('depot_lng').value = lng
        }
    }

    /*
    <div class="col-6 px-4">
        <label for="depot" class="form-label mb-0">Depot address</label>
        <input type="text" class="form-control" id="depot" name="depot"
            placeholder="Type and select the depot address">
        <input id="depot_lat" name="depot_lat" type="hidden">
        <input id="depot_lng" name="depot_lng" type="hidden">
    </div>
    */