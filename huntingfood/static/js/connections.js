function addInventoryItem(data) {
  console.log('addInventoryItem');

  var object = {
    'id': null,
    'title': data.title(),
    'uom_base': data.uom_base(),
    'uom_stock': data.uom_stock(),
    'material': data.material_id(),
    'quantity_base': data.quantity_base(),
    'quantity_conversion_factor': data.quantity_conversion_factor(),
    'quantity_stock': data.quantity_stock()
  }

  $.ajax({
    type: 'POST',
    url: url_api_inventory,
    contentType: 'application/json; charset=utf-8',
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    dataType: 'json',
    data: JSON.stringify(object),
    success: function(response) {

      // turn the json string into a javascript object
      var parsed = response['inventory_items']

      // for each iterable item create a new InventoryItem observable
      parsed.forEach( function(item) {
        invVM.inventoryItems.push( new InventoryItem(item) );
      });
    }
  });
}

function deleteInventoryItem(data) {
  console.log('deleteInventoryItem');

  var object = {
    'forecasts': {},
    'id': data.id(),
    'inventory': inv_id,
    'material': data.material_id(),
    'title': data.title()
  }

  $.ajax({
    type: 'DELETE',
    url: url_api_inventory,
    contentType: 'application/json; charset=utf-8',
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    dataType: 'json',
    data: JSON.stringify(object),
    success: function(response) {
      invVM.inventoryItems.remove(data);
    }
  });
}


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
