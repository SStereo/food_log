// adds a diet plan item into a day within the timeGrid
function addShoppingOrderItem(data) {
  console.log('addShoppingOrderItem');
  var now = new Date();

  var object = {
    'id': null,
    'material' : data.material_id(),
    'shopping_order' : data.shopping_order_id(),
    'quantity_purchased': data.quantity_purchased(),
    'in_basket' : data.in_basket(),
    'in_basket_time': now.toJSON(),
    'in_basket_geo_lat': null,
    'in_basket_geo_lon': null
  }

  $.ajax({
    type: 'POST',
    url: url_api_shopping_order_item,
    contentType: 'application/json; charset=utf-8',
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    dataType: 'json',
    data: JSON.stringify(object),
    success: function(response) {
      var parsed = response['shopping_order_item']
      data.id( parsed.id );
      console.log('new item created with id = ' + parsed.id);
    }
  });
}


function saveShoppingOrderItem(data) {
  console.log('saveShoppingOrderItem');
  var url = '';
  var method = '';
  var returnObject = null;

  // TODO: timestamp should be moved to backend functionality
  var now = new Date();

  // Handle both cases. One this function is called by the subscribe method
  // and this gets filled or via direct function call where newValue can
  // contain a full observable.
  //  if (!ko.isObservable(newValue)) {
  //  var data = this;
  //  } else {
  //  var data = newValue();
  //  }

  var object = {
    'id': data.id(),
    'material' : data.material_id(),
    'shopping_order' : data.shopping_order_id(),
    'quantity_purchased': data.quantity_purchased(),
    'in_basket' : data.in_basket(),
    'in_basket_time': now.toJSON(),
    'in_basket_geo_lat': null,
    'in_basket_geo_lon': null
  }

  $.ajax({
    type: 'PUT',
    url: url_api_shopping_order_item + '/' + data.id(),
    contentType: 'application/json; charset=utf-8',
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    dataType: 'json',
    data: JSON.stringify(object),
    success: function(response) {
      var parsed = response['shopping_order_item']

    }
  });
}
