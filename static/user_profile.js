function generateContent(marker) {
  console.log(marker);
  var content = '<h1>' + marker.city + ', ' + marker.country_name + '</h1>';
  content += '<p>Visited on ' + new Date(marker.timestamp * 1000).toString() + '</p>';
  return content;
}

function initMap() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', window.location.pathname + '/history');
  xhr.onload = function () {
    var marker_coords = JSON.parse(xhr.response).results;
    var markers = [];
    var map = new google.maps.Map(document.getElementById('locationHistoryMap'), {
      zoom: 2,
      center: {lat: 0, lng: 0}
    });
    var infowindow = new google.maps.InfoWindow({
        maxWidth: 500
    });
    for (var i = 0; i < marker_coords.length; i++) {
      var marker = new google.maps.Marker({
        position: {
          lat: marker_coords[i].lat,
          lng: marker_coords[i].lng,
        },
        map: map
      });
      markers.push(marker);
      google.maps.event.addListener(marker, 'click', (function(marker, markerInfo) {
        return function() {
          var content = generateContent(markerInfo);
          infowindow.setContent(content);
            infowindow.open(map, marker);
          }
      })(marker, marker_coords[i]));
    }
  };
  xhr.send();
}
