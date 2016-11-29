var placeSearch, autocomplete;
var componentForm = {
  locality: 'long_name',
  colloquial_area: 'long_name',
  administrative_area_level_1: 'long_name',
  administrative_area_level_2: 'long_name',
  country: 'long_name',
};

function initAutocomplete() {
  // Create the autocomplete object, restricting the search to geographical
  // location types.
  autocomplete = new google.maps.places.Autocomplete(
      /** @type {!HTMLInputElement} */(document.getElementById('citySelectorField')),
      {types: ['(cities)']});

  // When the user selects a city from the dropdown, populate the city
  // fields in the form.
  autocomplete.addListener('place_changed', fillInCity);
}

function fillInCity() {
  // Get the place details from the autocomplete object.
  var place = autocomplete.getPlace();

  for (var component in componentForm) {
    document.getElementById(component).value = '';
    document.getElementById(component).disabled = false;
  }

  // Get each component of the city from the place details
  // and fill the corresponding field on the form.
  var components = {}
  for (var i = 0; i < place.address_components.length; i++) {
    var addressType = place.address_components[i].types[0];
    if (componentForm[addressType]) {
      var val = place.address_components[i][componentForm[addressType]];
      document.getElementById(addressType).value = val;
      components[addressType] = val;
      if (addressType === 'country') {
        var country_code = place.address_components[i]['short_name']
        document.getElementById('country_code').value = country_code;
        components.country_code = country_code;
      }
    }
  }

  // added or hack because of Taipei
  var locationIndicatorText = (components.locality || components.colloquial_area) + ', ' + (components.administrative_area_level_1 || components.administrative_area_level_2) + ', ' + components.country;
  document.getElementById('locationIndicator').textContent = locationIndicatorText;
}

// Bias the autocomplete object to the user's geographical location,
// as supplied by the browser's 'navigator.geolocation' object.
function geolocate() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var geolocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      var circle = new google.maps.Circle({
        center: geolocation,
        radius: position.coords.accuracy
      });
      autocomplete.setBounds(circle.getBounds());
    });
  }
}

document.getElementById('mapGeneratorForm').onsubmit = function (e) {
  var form = this;
  var city = e.target.querySelector('input[name=city1]').value || e.target.querySelector('input[name=city2]').value;
  var region = e.target.querySelector('input[name=region1]').value || e.target.querySelector('input[name=region2]').value;
  var country_name = e.target.querySelector('input[name=country_name]').value;
  var country_code = e.target.querySelector('input[name=country_code]').value;
  if (!city || !region || !country_name || !country_code) {
    return false;
  }

  var params = 'city=' + encodeURIComponent(city) + '&country_name=' + encodeURIComponent(country_name) + '&country_code=' + encodeURIComponent(country_code);
  if (region) {
    // Make region optional (e.g. Singapore)
    params += ('&region=' + encodeURIComponent(region));
  }
  var img = document.createElement('img');
  img.src = '/map?' + params;
  img.onload = function () {
    document.getElementById('generatedImage').innerHTML = '';
    document.getElementById('generatedImage').appendChild(img);
    var user_id = form.dataset.userid;
    if (user_id) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', '/user/' + user_id + '/history');
      xhr.onload = function () {
        console.log('Updated user history');
      };
      xhr.send();
    }
  };

  var loading_font_size = '64px';
  document.getElementById('generatedImage').innerHTML = '';
  var spinner = document.createElement('i');
  spinner.classList.add('fa');
  spinner.classList.add('fa-spinner');
  spinner.classList.add('fa-spin');
  spinner.style['font-size'] = loading_font_size;
  document.getElementById('generatedImage').appendChild(spinner);
  var loading_text = document.createElement('p');
  loading_text.textContent = 'Loading...';
  loading_text.style['font-size'] = loading_font_size;
  document.getElementById('generatedImage').appendChild(loading_text);
  return false;
};
