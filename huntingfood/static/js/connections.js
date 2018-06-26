// adds a diet plan item into a day within the timeGrid
function addShoppingOrderItem(data) {

  console.log('addShoppingOrderItem');

  var now = new Date();

  var object = {
    'id': null,
    'material' : data.material_id(),
    'shopping_order' : data.shopping_order_id(),
    'quantity_purchased': 0,
    'in_basket' : true,
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
      data.currentShoppingOrderItem( new ShoppingOrderItem(parsed) );
      // console.log(data.shoppingOrderItem().in_basket_time());
    }
  });
}


function saveShoppingOrderItem(data) {

  console.log('saveShoppingOrderItem');

  // TODO: timestamp should be moved to backend functionality
  var now = new Date();

  var object = {
    'id': data.id(),
    'material' : data.material_id(),
    'shopping_order' : data.shopping_order_id(),
    'quantity_purchased': 0,
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
      data( new ShoppingOrderItem(parsed) );
      // console.log(data.shoppingOrderItem().in_basket_time());
    }
  });
}
