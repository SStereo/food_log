
  function slLoadItems() {
    $.ajax({
      type: 'GET',
      url: url_sl_items,
      dataType: 'json',
      success: slCreateElements // name of function that processes the response
    });
  }


  function dpLoadItems() {
    $.ajax({
      type: 'GET',
      url: url_dp_items,
      dataType: 'json',
      data: {'diet_plan_id' : dp_id},
      success: dpUpdateElements // name of function that processes the response
    });
  }


  function dpUpdateElements(response) {

    var n;
    var elSelector;

    var obj = "diet_plan_items";
    var key_names = ["diet_plan_id", "meal_id"];
    var key_values = [];
    var data_fields = ["planned", "consumed", "plan_date", "portions"]; // "plan_date", "portions",
    var data_element;

    // Determine number or records
    n = response['diet_plan_items'].length;

    for (var i = 0; i < n; i++) {
      // Get Keys
      meal_id = response['diet_plan_items'][i]['meal_id'];
      diet_plan_id = response['diet_plan_items'][i]['diet_plan_id'];

      key_values = [];
      for (var x = 0; x < key_names.length; x++) {
        key_values.push(response[obj][i][key_names[x]]);
      }

      for (var y = 0; y < data_fields.length; y++) {
        data_value = response[obj][i][data_fields[y]];
        elSelector = "[data-key1='".concat(key_values[0],"'][data-key2='",key_values[1],"'][data-field='",data_fields[y],"']");
        console.log(elSelector);
        data_element = $(elSelector);

        SetElementValue(data_element, data_value);
      }

    }
    console.log("Update successful");
  }


  function SetElementValue (data_element, data_value) {
    if (data_element.attr("type") == "checkbox") {
      data_element.attr("checked", data_value);;
    }
    else if (data_element.attr("type") == "text"){
      data_element.val(data_value);
    }
    else if (data_element.prop("tagName") == "SELECT"){
      var elOption = data_element.find("option[value="+ data_value + "]");
      elOption.attr('selected',true);
      // console.log(elOption.attr('selected'));
      data_element.val(data_value.toString());
    }

  }


  function dpSaveItem() {

    var data_field = $(this).attr("name");
    if ($(this).attr("type") == "checkbox") {
      var data_value = $(this).prop("checked");
    }
    else {
      var data_value = $(this).val();
    }

    var diet_plan_id = parseInt($(this).attr("data-key1"));
    var meal_id = parseInt($(this).attr("data-key2"));

    console.log(meal_id);
    console.log(data_field);
    console.log(data_value);
    method = 'POST'
    dataObj = {
      'diet_plan_id' : diet_plan_id,
      'meal_id' : meal_id,
      'FIELD' : data_field,
      'VALUE' : data_value
    };
    $.ajax({
      type: method,
      url: url_dp_items,
      dataType: 'json',
      data: dataObj,
      success: function() {
        console.log("Field saved successfullly.");
      } // name of function that processes the response
    });

  }


  function slSaveData() {
    var messageDiv = $('#sl-messages');
    var inputData = $('#sl-new-item').val();

    if (inputData === '') {
      alert("You must write something!");
    } else {

      $.ajax({
        type: 'POST',
        url: url_sl_items,
        dataType: 'json',
        data: {'title' : inputData},
        success: slCreateElements // name of function that processes the response
      });
    }
  }


  function slDeleteItem() {
    var itemrow = this.parentElement;
    elId = itemrow.id;

    $.ajax({
      type: 'DELETE',
      url: url_sl_items,
      dataType: 'text',
      data: {'id' : elId},
      success: function() {
        itemrow.style.display = "none";
      }
    });
  }


  function slCreateElements(response) {
    var items = document.getElementById("sl-items");
    var n;
    n = response['inventory_items'].length;

    for (var i = 0; i < n; i++) {
      itemValue = response['inventory_items'][i]['titleDE'];
      itemId = response['inventory_items'][i]['id'];
      // Create new Item HTML
      var itemrow = document.createElement("DIV");
      itemrow.className = "sl-form";
      itemrow.id = itemId;

      var elInput = document.createElement("INPUT");
      elInput.value = itemValue;
      elInput.type = "text"
      elInput.className = "form-control sl-item";

      var elButton = document.createElement("BUTTON");
      elButton.className = "btn btn-default sl-btn";
      elButton.onclick = slDeleteItem;

      var elIcon = document.createElement("i");
      elIcon.className = "fa fa-trash mr-1";

      elButton.appendChild(elIcon);
      itemrow.appendChild(elInput);
      itemrow.appendChild(elButton);
      items.appendChild(itemrow);
    };

    // TODO: wrong place should not apply for page load
    document.getElementById("sl-new-item").value = "";

  }



// +++++++++++++++++++++++++++
// MAP
// +++++++++++++++++++++++++++

var map;
var markers = []; // for all known places from the database
var search_markers = [];

function mapLoadPlaces() {
  $.ajax({
    type: 'GET',
    url: url_map_items,
    dataType: 'json',
    success: function(response) {
      var largeInfowindow = new google.maps.InfoWindow();
      var bounds = new google.maps.LatLngBounds();
      var places = response['places']
      var n = places.length;
      for (var i = 0; i < n; i++) {
        var position = {lat: places[i].geo_lat, lng: places[i].geo_lng};
        var title = places[i].titleDE;
        var marker = new google.maps.Marker({
          map: map,
          position: position,
          title: title,
          animation: google.maps.Animation.DROP,
          id: i
        });
        markers.push(marker);
        bounds.extend(marker.position);
        marker.addListener('click', function() {
          mapPopulateInfoWindow(this, largeInfowindow);
        });
      }
    map.fitBounds(bounds);
    }
  });
}


function mapShowPlace(place) {
  var largeInfowindow = new google.maps.InfoWindow();
  var bounds = new google.maps.LatLngBounds();
  var position = {lat: place.geo_lat, lng: place.geo_lng};
  var title = place.name;
  var marker = new google.maps.Marker({
      map: map,
      position: position,
      title: title,
      animation: google.maps.Animation.DROP,
      id: search_markers.length + 1
  });
  search_markers.push(marker);
  bounds.extend(marker.position);
  marker.addListener('click', function() {
    mapPopulateInfoWindow(this, largeInfowindow);
  });
  map.fitBounds(bounds);
}


function mapMakeMarkerIcon(markerColor) {
  var markerImage = new google.maps.MarkerImage(
    'http://chart.googleapis.com/chart?chst=d_map_spin&chld=1.15|0|'+markerColor +
    '|40|_|%E2%80%A2',
    new google.maps.Size(21, 34),
    new google.maps.Point(0, 0),
    new google.maps.Point(10, 34),
    new google.maps.Size(21, 34));
  return markerImage
}


function mapPopulateInfoWindow(marker, infowindow) {
  if (infowindow.marker != marker) {
    infowindow.marker = marker;
    infowindow.setContent('<div>' + marker.title + '</div>');
    infowindow.open(map, marker);
    // Make sure the marker property is cleared if the infowindo is closed.
    infowindow.addListener('closeclick', function() {
      infowindow.setMarker(null);
    });
  }
}


function mapGeolocate(autocomplete) {
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
      return geolocation
    });
  }
}


function initMap() {
  var styledMapType = new google.maps.StyledMapType(
          [
            {elementType: 'geometry', stylers: [{color: '#ebe3cd'}]},
            {elementType: 'labels.text.fill', stylers: [{color: '#523735'}]},
            {elementType: 'labels.text.stroke', stylers: [{color: '#f5f1e6'}]},
            {
              featureType: 'administrative',
              elementType: 'geometry.stroke',
              stylers: [{color: '#c9b2a6'}]
            },
            {
              featureType: 'administrative.land_parcel',
              elementType: 'geometry.stroke',
              stylers: [{color: '#dcd2be'}]
            },
            {
              featureType: 'administrative.land_parcel',
              elementType: 'labels.text.fill',
              stylers: [{color: '#ae9e90'}]
            },
            {
              featureType: 'landscape.natural',
              elementType: 'geometry',
              stylers: [{color: '#dfd2ae'}]
            },
            {
              featureType: 'poi',
              elementType: 'geometry',
              stylers: [{color: '#dfd2ae'}]
            },
            {
              featureType: 'poi',
              elementType: 'labels.text.fill',
              stylers: [{color: '#93817c'}]
            },
            {
              featureType: 'poi.park',
              elementType: 'geometry.fill',
              stylers: [{color: '#a5b076'}]
            },
            {
              featureType: 'poi.park',
              elementType: 'labels.text.fill',
              stylers: [{color: '#447530'}]
            },
            {
              featureType: 'road',
              elementType: 'geometry',
              stylers: [{color: '#f5f1e6'}]
            },
            {
              featureType: 'road.arterial',
              elementType: 'geometry',
              stylers: [{color: '#fdfcf8'}]
            },
            {
              featureType: 'road.highway',
              elementType: 'geometry',
              stylers: [{color: '#f8c967'}]
            },
            {
              featureType: 'road.highway',
              elementType: 'geometry.stroke',
              stylers: [{color: '#e9bc62'}]
            },
            {
              featureType: 'road.highway.controlled_access',
              elementType: 'geometry',
              stylers: [{color: '#e98d58'}]
            },
            {
              featureType: 'road.highway.controlled_access',
              elementType: 'geometry.stroke',
              stylers: [{color: '#db8555'}]
            },
            {
              featureType: 'road.local',
              elementType: 'labels.text.fill',
              stylers: [{color: '#806b63'}]
            },
            {
              featureType: 'transit.line',
              elementType: 'geometry',
              stylers: [{color: '#dfd2ae'}]
            },
            {
              featureType: 'transit.line',
              elementType: 'labels.text.fill',
              stylers: [{color: '#8f7d77'}]
            },
            {
              featureType: 'transit.line',
              elementType: 'labels.text.stroke',
              stylers: [{color: '#ebe3cd'}]
            },
            {
              featureType: 'transit.station',
              elementType: 'geometry',
              stylers: [{color: '#dfd2ae'}]
            },
            {
              featureType: 'water',
              elementType: 'geometry.fill',
              stylers: [{color: '#11d3c2'}]
            },
            {
              featureType: 'water',
              elementType: 'labels.text.fill',
              stylers: [{color: '#92998d'}]
            }
          ],
          {name: 'Styled Map'});

  // Map
  console.log("Running map");

  // autocomplete for the search inbox
  var input = document.getElementById('search'); //$('#search');
  var options = {
    types: ['establishment']  // only one parameter is allowed
  };
  var searchAutocomplete = new google.maps.places.Autocomplete(input, options);

  // identifies user location and sets autocomplete bounds and current position
  // TODO: Determine best way to bound autocomplete, further down is another one
  var current_position = mapGeolocate(searchAutocomplete);

  map = new google.maps.Map(document.getElementById('map'), {
    center: current_position,
    zoom: 14,
    mapTypeControlOptions: {
       mapTypeIds: ['roadmap', 'satellite', 'styled_map']
    }
  });

  searchAutocomplete.bindTo('bounds', map);

  //TODO: fix this so it shows the search result in a different marker style
  searchAutocomplete.addListener('place_changed', function() {
    var places = this.getPlaces();
    mapShowPlace(places[0]);
  });

  //Associate the styled map with the MapTypeId and set it to display.
   map.mapTypes.set('styled_map', styledMapType);
   map.setMapTypeId('styled_map');

  // Marker, TODO: Add search criteria so that only nearby points are shown
  mapLoadPlaces();

  // InfoWindows

  // event listener for InfoWindows

}
