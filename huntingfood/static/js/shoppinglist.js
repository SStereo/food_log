'use strict';
// Returns the ISO week of the date.
// source: https://weeknumber.net/how-to/javascript
var DateGetWeek = function(d) {
  var date = new Date(d.getTime());
  date.setHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
  // January 4 is always in week 1.
  var week1 = new Date(date.getFullYear(), 0, 4);
  // Adjust to Thursday in week 1 and count number of weeks from date to week1.
  return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000
                        - 3 + (week1.getDay() + 6) % 7) / 7);
}

// Compares two time periods and determines the number of days overlap
var DaysOverlap = function(d0_start, d0_end, d1_start, d1_end) {
  var days = 0
  var timeDiff = 0;
  if (d0_start.getTime() >= d1_start.getTime() && d1_end.getTime() > d0_start.getTime()) {
    if (d0_end.getTime() <= d1_end.getTime()) {
      timeDiff = Math.abs(d0_end.getTime() - d0_start.getTime());
      days = Math.ceil(timeDiff / (1000 * 3600 * 24));
    } else if (d0_end.getTime() > d1_end.getTime()) {
      timeDiff = Math.abs(d1_end.getTime() - d0_start.getTime());
      days = Math.ceil(timeDiff / (1000 * 3600 * 24));
    };
  } else if (d0_start.getTime() < d1_start.getTime() && d1_start.getTime() < d0_end.getTime()) {
    if (d0_end.getTime() <= d1_end.getTime()) {
      timeDiff = Math.abs(d0_end.getTime() - d1_start.getTime());
      days = Math.ceil(timeDiff / (1000 * 3600 * 24));
    } else if (d0_end.getTime() > d1_end.getTime()) {
      timeDiff = Math.abs(d1_end.getTime() - d1_start.getTime());
      days = Math.ceil(timeDiff / (1000 * 3600 * 24));
    };
  } else {
    days = 0;
  };

  return days;
}


  function slLoadItems() {
    $.ajax({
      type: 'GET',
      url: url_sl_items,
      dataType: 'json',
      success: slCreateElements // name of function that processes the response
    });
  }


  function slSaveData() {
    var messageDiv = $('#sl-messages');
    var inputData = $('#sl-new-item').val();

    if (inputData === '') {
      alert('You must write something!');
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
        itemrow.style.display = 'none';
      }
    });
  }


  function slCreateElements(response) {
    var items = document.getElementById('sl-items');
    var n;
    var itemValue = '';
    var itemId = '';
    n = response['inventory_items'].length;

    for (var i = 0; i < n; i++) {
      itemValue = response['inventory_items'][i]['title'];
      itemId = response['inventory_items'][i]['id'];
      // Create new Item HTML
      var itemrow = document.createElement('DIV');
      itemrow.className = 'sl-form';
      itemrow.id = itemId;

      var elInput = document.createElement('INPUT');
      elInput.value = itemValue;
      elInput.type = 'text'
      elInput.className = 'form-control sl-item';

      var elButton = document.createElement('BUTTON');
      elButton.className = 'btn btn-default sl-btn';
      elButton.onclick = slDeleteItem;

      var elIcon = document.createElement('i');
      elIcon.className = 'fa fa-trash mr-1';

      elButton.appendChild(elIcon);
      itemrow.appendChild(elInput);
      itemrow.appendChild(elButton);
      items.appendChild(itemrow);
    };

    // TODO: wrong place should not apply for page load
    document.getElementById('sl-new-item').value = '';

  }


  // KNOCKOUT FRAMEWORK IMPLEMENTATION

  // VIEW MODEL
var dpViewModel = function() {
  var self = this;

  self.meals = ko.observableArray([]);
  self.weekSelected = ko.observable('');
  self.weekRange = ko.observableArray([]);
  self.portions = ko.observableArray([1,2,3,4,5,6,7,8,9,10,11,12]);
  self.userSettings = ko.observable('');

  self.loadMeals = function() {
    $.ajax({
      type: 'GET',
      url: url_api_meals,
      dataType: 'json',
      success: function(response) {
        var parsed = response['meals']
        parsed.forEach( function(item) {
          self.meals.push( new Meal(item) );
        });
      }
    });
  }

  self.loadUserData = function() {
    $.ajax({
      type: 'GET',
      url: url_api_users,
      dataType: 'json',
      success: function(response) {
        var parsed = response['users']
        parsed.forEach( function(item) {
          self.userSettings( new User(item) );
        });
      }
    });
  }

  self.changeWeek = function(data, event) {
    self.weekSelected(data.week_index());
    self.loadDietPlanItems();
  }

  self.initGrid = function() {
    var date_range = [];
    var item = '';
    var d_string = '';
    var now = new Date();  // current date & time local time zone
    var today = new Date(now.getFullYear(),now.getMonth(), now.getDate(), 0, 0, 0, 0); // returns current date in UTC
    today.setHours(0,0,0,0);
    var d = new Date(today.getTime());  // create a copy of today
    const week_range_max = 3;
    const num_days = 7;

    console.log('now (UTC) = ' + now.toUTCString());
    console.log('today (local) = ' + today);
    console.log('today (UTC) = ' + today.toJSON());

    // Determine date of first day of the current week
    var today_weekday = (today.getDay() + 6) % 7; // monday is fist not sunday
    d.setDate(today.getDate() - today_weekday);
    console.log('today.getDate() = ' + today.getDate());
    console.log('d = ' + d);
    // Make first week the default selected one
    self.weekSelected(0);  // TODO: Find a better way for filtering

    // ++++++ Generate Week Objects +++++
    var d2 = new Date(d.getTime());
    for (var i = 0; i < week_range_max; i++) {
      date_range = [];
      // after the first week increment the start day by 7 days
      if (i > 0) {
        d2.setDate(d2.getDate() + 7);
      }

      // Copy start date into other variable
      var d3 = new Date(d2.getTime());

      // Determine all days of week
      d3.setDate(d3.getDate() - 1);
      for (var y = 0; y < num_days; y++) {
        d3.setDate(d3.getDate() + 1);
        console.log('Days of Week = ' + d3);

        // TODO: Why a string?
        // d_string = d3.getFullYear() + '-' + (d3.getMonth() + 1) + '-' + d3.getDate();
        // date_range.push(d_string);
        date_range.push(d3.toJSON());
      }

      console.log('d2.getTime() = ' + d2.getTime())
      // Create a new GridWeek object with initial meta data (item)
      item = {
        week_number: DateGetWeek(d2),
        index: i,  // TODO: remove once filter is improved
        date_first_day: d2.getTime(),
        date_range: date_range
      }

      var grid_week = new GridWeek(item);
      self.weekRange.push(grid_week);

      // Create GridDay objects for each day in the date range
      grid_week.date_range().forEach( function(item) {
        var grid_day = new GridDay(item);
        grid_week.grid_days.push( grid_day )
      })

    }
    // +++++++++++++++++++++++
  }

  self.loadDietPlanItems = function() {
    var index = self.weekSelected();
    self.weekRange()[index].grid_days().forEach( function(item) {
      // Deletes all dietPlanObjects prior of loading them fresh from the server
      item.dietPlanItems.removeAll();

      var plan_date = new Date(item.date())
      // Loads data from the REST API
      $.ajax({
        type: 'GET',
        url: url_api_dietplan,
        dataType: 'json',
        data: {
          'plan_date' : plan_date.toJSON()
        },
        success: function(response) {
          // turn the json string into a javascript object
          var parsed = response['diet_plan_items'] // JSON.parse(response['diet_plan_items']);
          // for each iterable item create a new DietPlanItem observable
          parsed.forEach( function(object) {
            item.dietPlanItems.push( new DietPlanItem(object) );
          });
        }
      });
    });
  }

  self.removeDietPlanItem = function(parent, data, event) {
    console.log('removeDietPlanItem(meal_id=' + data.meal_id() + ')');

    var plan_date = new Date(data.plan_date())

    $.ajax({
      type: 'DELETE',
      url: url_api_dietplan,
      dataType: 'json',
      data: {
        'id' : data.id(),
        'diet_plan_id' : dp_id,
        'meal_id' : data.meal_id(),
        'plan_date' : plan_date.toJSON()
      },
      headers: {
        'X-CSRFTOKEN' : csrf_token
      },
      success: function(response) {
        parent.dietPlanItems.remove(data);
      }
    });
  }

  // adds a diet plan item into a day within the timeGrid
  self.addDietPlanItem = function(data, event) {

    console.log('addDietPlanItem: plan_date = ' + data.date() + ')');

    var plan_date = new Date(data.date());
    console.log(' var plan_date = ' + plan_date);
    $.ajax({
      type: 'POST',
      url: url_api_dietplan,
      headers: {
        'X-CSRFTOKEN' : csrf_token
      },
      dataType: 'json',
      data: {
        'diet_plan_id' : dp_id,
        'meal_id' : data.meal_id_select2add(),
        'plan_date' : plan_date.toJSON(),
        'portions' : self.userSettings().default_portions()
      },
      success: function(response) {

        // turn the json string into a javascript object
        var parsed = response['diet_plan_item']

        // for each iterable item create a new DietPlanItem observable
        parsed.forEach( function(item) {
          data.dietPlanItems.push( new DietPlanItem(item) );
        });
      }
    });

  }

  self.getMealImageURL = function(meal_id) {
    var m = '';
    m = self.meals().find( function(item) {
      return item.id() == meal_id();
    });
    if (m) {
      console.log('getMealImageURL(' + meal_id() + ') = '  + m.image());
      return m.image();
    } else {
      return ''
    }
  }

  // Initialization
  self.loadUserData();
  self.loadMeals();
  self.initGrid();
  self.loadDietPlanItems();

  self.selectedGridWeek = ko.computed(function() {
    // Sets the selected week by filtering on the index
    var index = self.weekSelected();
    return ko.utils.arrayFilter(self.weekRange()[index].grid_days(), function(item) {
      return true;
    });

    // TODO: This is NOT WORKING
    var array = ko.utils.arrayFilter(self.weekRange(), function(item) {
      if (item.week_number() == self.weekSelected()) {
        return true;
      } else {
        return false;
      }
    });
    return array.grid_days;

  })

}

// This callback function is called whenever a subscription event on observables are triggered
// TODO: this is the only CRUD function sitting outside of the ViewModel -> fix
function saveDietPlanItem(newValue) {
  console.log('saveDietPlanItem: plan_date = ' + this.plan_date());

  var plan_date = new Date(this.plan_date())

  $.ajax({
    type: 'PUT',
    url: url_api_dietplan,
    dataType: 'json',
    data: {
      'id' : this.id(),
      'diet_plan_id' : dp_id,
      'meal_id' : this.meal_id(),
      'plan_date' : plan_date.toJSON(),
      'consumed' : this.consumed(),
      'portions' : this.portions()
    },
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    success: function(response) {
      //TODO: undo changes in case of failure
      console.log('saveDietPlanItem: success');
    }
  });

}

var User = function(data) {
  this.user_id = ko.observable(data.user_id);
  this.name = ko.observable(data.name);
  this.picture = ko.observable(data.picture);
  this.default_portions = ko.observable(data.default_portions);
  this.default_diet_plan_id = ko.observable(data.default_diet_plan_id);
  this.default_inventory_id = ko.observable(data.default_inventory_id);
}


var Meal = function(data) {
  this.id = ko.observable(data.id);
  this.title = ko.observable(data.title);
  this.description = ko.observable(data.description);
  this.portions = ko.observable(data.portions);
  this.rating = ko.observable(data.rating);
  this.image = ko.observable(data.image);
}

var GridWeek = function(data) {
  this.week_number = ko.observable(data.week_number);
  this.week_index = ko.observable(data.index); // TODO: remove once filter is improved
  this.date_first_day = ko.observable(data.date_first_day);
  this.date_range = ko.observableArray(data.date_range);
  this.grid_days = ko.observableArray([]);
}

var GridDay = function(data) {
  this.date = ko.observable(data);
  this.dayShort = ko.pureComputed(function() {
    var d = new Date(this.date());
    return d.toDateString()
  }, this);
  this.dietPlanItems = ko.observableArray([]);
  this.meal_id_select2add = ko.observable();
}

var DietPlanItem = function(data) {
  this.id = ko.observable(data.id);
  this.diet_plan_id = ko.observable(data.diet_plan_id);
  this.meal_id = ko.observable(data.meal_id);
  this.meal_id.subscribe(saveDietPlanItem, this);
  this.plan_date = ko.observable(data.plan_date);
  this.plan_date.subscribe(saveDietPlanItem, this);
  this.portions = ko.observable(data.portions);
  this.portions.subscribe(saveDietPlanItem, this);
  this.consumed = ko.observable(data.consumed);
  this.consumed.subscribe(saveDietPlanItem, this);
}


// ++++++++++++++++++++++++++ INVENTORY +++++++++++++++++++++++++++++++++++++++
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

var ENTER_KEY = 13;
var ESCAPE_KEY = 27;

// A factory function we can use to create binding handlers for specific
// keycodes.
function keyhandlerBindingFactory(keyCode) {
	return {
		init: function (element, valueAccessor, allBindingsAccessor, data, bindingContext) {
			var wrappedHandler, newValueAccessor;

			// wrap the handler with a check for the enter key
			wrappedHandler = function (data, event) {
				if (event.keyCode === keyCode) {
					valueAccessor().call(this, data, event);
				}
			};

			// create a valueAccessor with the options that we would want to pass to the event binding
			newValueAccessor = function () {
				return {
					keyup: wrappedHandler
				};
			};

			// call the real event binding's init function
			ko.bindingHandlers.event.init(element, newValueAccessor, allBindingsAccessor, data, bindingContext);
		}
	};
}

// a custom binding to handle the enter key
ko.bindingHandlers.enterKey = keyhandlerBindingFactory(ENTER_KEY);

// another custom binding, this time to handle the escape key
ko.bindingHandlers.escapeKey = keyhandlerBindingFactory(ESCAPE_KEY);

// wrapper to hasFocus that also selects text and applies focus async
ko.bindingHandlers.selectAndFocus = {
	init: function (element, valueAccessor, allBindingsAccessor, bindingContext) {
		ko.bindingHandlers.hasFocus.init(element, valueAccessor, allBindingsAccessor, bindingContext);
		ko.utils.registerEventHandler(element, 'focus', function () {
			element.focus();
		});
	},
	update: function (element, valueAccessor) {
		ko.utils.unwrapObservable(valueAccessor()); // for dependency
		// ensure that element is visible before trying to focus
		setTimeout(function () {
			ko.bindingHandlers.hasFocus.update(element, valueAccessor);
		}, 0);
	}
};

// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// Custom binding for a modal bootstrap dialogs
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ko.bindingHandlers['modal'] = {
  init: function(element, valueAccessor, allBindingsAccessor) {
    var allBindings = allBindingsAccessor();
    var $element = $(element);
    $element.addClass('hide modal');

    if (allBindings.modalOptions && allBindings.modalOptions.beforeClose) {
      $element.on('hide', function() {
        var value = ko.utils.unwrapObservable(valueAccessor());
        return allBindings.modalOptions.beforeClose(value);
      });
    }
  },
  update: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());
    if (value) {
      $(element).removeClass('hide').modal('show');
    } else {
      $(element).modal('hide');
    }
  }
};


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// AJAX functions
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

function saveInventoryItem(newValue) {

  var currentItem = this;

  if (this.suspend_backend_update()) {
    console.log('saveInventoryItem: suspended');
    return false;
  }

  var cp_plan_date_start = new Date(this.cp_plan_date_start());
  var cp_plan_date_end = new Date(this.cp_plan_date_end());
  var op_plan_date_start = new Date(this.op_plan_date_start());
  var op_plan_date_end = new Date(this.op_plan_date_end());

  var object = {
          'cp_day_in_month': this.cp_day_in_month(),
          'cp_end_date': null,
          'cp_period': this.cp_period(),
          'cp_plan_date': null,
          'cp_plan_date_end': cp_plan_date_end.toJSON(),
          'cp_plan_date_start': cp_plan_date_start.toJSON(),
          'cp_quantity': this.cp_quantity(),
          'cp_type': this.cp_type(),
          'forecasts': {},
          'id': this.id(),
          'ignore_forecast': this.ignoreForecast(),
          'inventory': inv_id,
          'level': null,
          'material': this.material_id(),
          'op_plan_date_end': op_plan_date_end.toJSON(),
          'op_plan_date_start': op_plan_date_start.toJSON(),
          'op_quantity': this.op_quantity(),
          'quantity_base': this.quantity_base(),
          'quantity_conversion_factor': this.quantity_conversion_factor(),
          'quantity_stock': this.quantity_stock(),
          're_order_level': this.re_order_level(),
          're_order_quantity': this.re_order_quantity(),
          'title': this.title(),
          'titleEN': null,
          'uom_base': this.uom_base(),
          'uom_stock': this.uom_stock()
        }

  if (this.id()) {
    $.ajax({
      type: 'PUT',
      url: url_api_inventory,
      contentType: 'application/json; charset=utf-8',
      headers: {
        'X-CSRFTOKEN' : csrf_token
      },
      dataType: 'json',
      data: JSON.stringify(object),
      success: function(response) {
        //TODO: undo changes in case of failure

        // Updates forecast from response JSON since changes are calculated
        // on the backend
        var parsed = response['inventory_items'];
        currentItem.forecasts.removeAll();
        parsed.forEach( function(item) {
          currentItem.forecasts(ko.utils.arrayMap(item.forecasts, function(forecast) {
            return new MaterialForecast(forecast);
          }));
        });

        console.log('saveInventoryItem: success');
      }
    });
  }
}

var invViewModel = function() {
  var self = this;
  this.inventoryItems = ko.observableArray([]);
  const default_forecast_days = 7;
  const default_plan_date_end = '2028-06-03T22:00:00+00:00'
  this.planForecastDays = ko.observable(default_forecast_days);

  self.plan_date_start = ko.observable( new Date() );
  self.plan_date_end = ko.computed( function() {
    var dateTo = new Date(self.plan_date_start()); //new Date();
    dateTo.setDate(dateTo.getDate() + parseInt(self.planForecastDays()));
    return dateTo;
  } );

  // Reference Data
  self.materials = ko.observableArray([]);
  self.unitsOfMeasure = ko.observableArray([]);

  // store the new Inventory value being entered
	this.newInventoryItemTitle = ko.observable();
  this.newInventoryItemBaseUnit = ko.observable();
  this.newInventoryItemStockUnit = ko.observable();
  self.showControls = ko.computed( function() {
    console.log('title = ' + self.newInventoryItemTitle());
    if (self.newInventoryItemTitle() === undefined) {
      console.log('hide control');
      return 'hide-control';
    } else {
      console.log('show control');
      return 'show-control';
    }
  });

  this.cpTypes = ko.observableArray([
    {'id': 0, 'TextDE': 'nein'},
    {'id': 1, 'TextDE': 'täglich'},
    {'id': 2, 'TextDE': 'einmal pro Woche'},
    {'id': 3, 'TextDE': 'einmal pro Monat'},
    {'id': 4, 'TextDE': 'einmal im Jahr'}
  ]);

  // Required for modal: The instance of the item currently being edited.
  self.ItemBeingEdited = ko.observable();
  self.ItemBeingEdited2 = ko.observable();
  self.ItemBeingEdited3 = ko.observable();
  self.ItemBeingEdited4 = ko.observable();


  // Required for modal: Used to keep a reference back to the original user record being edited
  self.OriginalItemInstance = ko.observable();

  this.ValidationErrors = ko.observableArray([]);

  this.filterStatus = ko.observable('all');

  this.filteredInventoryItems = ko.computed(function () {
			switch (self.filterStatus()) {
			case '0':
				return self.inventoryItems().filter(function (item) {
					return item.status() == 0;
				});
			case '1':
				return self.inventoryItems().filter(function (item) {
					return item.status() == 1;
				});
      case '2':
				return self.inventoryItems().filter(function (item) {
					return item.status() == 2;
				});
      case '3':
        return self.inventoryItems().filter(function (item) {
          return item.status() == 3;
        });
			default:
				return self.inventoryItems();
			}
		});


  // Loads inventory items from Rest API
  self.loadUnitsOfMeasure = function() {
    self.unitsOfMeasure.removeAll();
    console.log('Loading units of measures ...');
    $.ajax({
      type: 'GET',
      url: url_api_uom,
      dataType: 'json',
      success: function(response) {
        var parsed = response['uoms']
        parsed.forEach( function(item) {
          self.unitsOfMeasure.push( new UnitOfMeasure(item) );
        });
      }
    });
  };

  self.loadMaterials = function(searchTerm, callback) {
    $.ajax({
      dataType: 'json',
      url: url_api_materials,
      data: {
        query: searchTerm
      },
    }).done(callback);
  };

  // Loads inventory items from Rest API
  self.loadInventoryItems = function() {
    self.inventoryItems.removeAll();
    console.log('Loading inventory items ...');
    $.ajax({
      type: 'GET',
      url: url_api_inventory,
      dataType: 'json',
      success: function(response) {
        var parsed = response['inventory_items']
        parsed.forEach( function(item) {
          self.inventoryItems.push( new InventoryItem(item) );
        });
      }
    });
  };

  // Removes inventory items via Rest API
  self.removeInventoryItem = function(data, event) {
    $.ajax({
      type: 'DELETE',
      url: url_api_inventory,
      dataType: 'json',
      data: {
        'id' : data.id()
      },
      headers: {
        'X-CSRFTOKEN' : csrf_token
      },
      success: function(response) {
        self.inventoryItems.remove(data);
      }
    });
  };

  self.toogleStatus = function(data, event) {
    var statusText = '';
    switch (data.status()) {
      case 0:
        data.ignoreForecast(false);
        data.quantity_base(0);
        statusText = '0%';
        break;
      case 1:
        if (data.quantity_base_user() < data.plannedQuantityTotal() && data.quantity_base_user() != 0 && data.quantity_base_user() != null) {
          data.quantity_base(data.quantity_base_user());
        } else {
          data.quantity_base(data.plannedQuantityTotal()/2);
        }
        statusText = Math.round(data.quantity_base() / data.plannedQuantityTotal() * 100) + '%';
        break;
      case 2:
        if (data.quantity_base_user() > data.plannedQuantityTotal()) {
          data.quantity_base(data.quantity_base_user());
        } else {
          data.quantity_base(data.plannedQuantityTotal());
        }
        statusText = Math.round(data.quantity_base() / data.plannedQuantityTotal() * 100) + '%';
        break;
      case 3:
        data.ignoreForecast(true);
        statusText = 'zZ';
    };
    data.statusText(statusText);

  };

  // adds a inventory item
  self.addInventoryItem = function(data, event) {

    var title = self.newInventoryItemTitle();
    var uom_base_id = self.newInventoryItemBaseUnit();
    var uom_stock_id = self.newInventoryItemStockUnit();
    if (title) {
      if (isNaN(title)) {
        var material_id = null;
        title = title.trim();
      } else {
        var material_id = title;
        var title = '';
      }
      console.log('addInventoryItem');

      var object = {
        'id': null,
        'quantity_base': 0,
        'quantity_conversion_factor': 200,
        'quantity_stock': 0,
        'title': title,
        'uom_base': uom_base_id,
        'uom_stock': uom_stock_id,
        'material': material_id
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

          // for each iterable item create a new DietPlanItem observable
          parsed.forEach( function(item) {
            self.inventoryItems.push( new InventoryItem(item) );
          });
        }
      });
    }
    self.newInventoryItemTitle('');
  };

  // Required for modal: Validate data
  self.ValidateInventoryItem = function(item) {
    if (!item) {
      return false;
    }

    var currentItem = ko.utils.unwrapObservable(item);
    var currentQuantityBase = ko.utils.unwrapObservable(currentItem.quantity_base);
    var currentTitle = ko.utils.unwrapObservable(currentItem.title);
    var currentReOrderLevel = ko.utils.unwrapObservable(currentItem.re_order_level);

    self.ValidationErrors.removeAll(); // Clear out any previous errors

    // add checks

    return self.ValidationErrors().length <= 0;
  };

  // Required for modal: Validate data
  self.ValidateInventoryItem2 = function(item) {
    if (!item) {
      return false;
    }

    var currentItem = ko.utils.unwrapObservable(item);
    var quantityBase = ko.utils.unwrapObservable(currentItem.quantity_base);
    var quantityStock = ko.utils.unwrapObservable(currentItem.quantity_stock);

    self.ValidationErrors.removeAll(); // Clear out any previous errors

    if (quantityBase === null) {
      self.ValidationErrors.push('Bestand wird benötigt.');
    } else { // Just some arbitrary checks here...
        if (quantityBase < 0) {
          self.ValidationErrors.push('Bestand muß 0 oder größer sein.');
        }
    }

    if (quantityStock === null) {
      self.ValidationErrors.push('Lagerbestand wird benötigt.');
    } else { // Just some arbitrary checks here...
        if (quantityStock < 0) {
          self.ValidationErrors.push('Lagerbestand muß 0 oder größer sein.');
        }
    }

    return self.ValidationErrors().length <= 0;
  };

  // Required for modal: Validate data
  self.ValidateInventoryItem3 = function(item) {
    if (!item) {
      return false;
    }

    var currentItem = ko.utils.unwrapObservable(item);
    var title = ko.utils.unwrapObservable(currentItem.title);
    var uom_base = ko.utils.unwrapObservable(currentItem.uom_base);
    var uom_stock = ko.utils.unwrapObservable(currentItem.uom_stock);
    var quantity_conversion_factor = ko.utils.unwrapObservable(currentItem.quantity_conversion_factor);

    self.ValidationErrors.removeAll(); // Clear out any previous errors

    if (!title) {
      self.ValidationErrors.push('Please enter a title for the item');
    }

    if (quantity_conversion_factor === null) {
      self.ValidationErrors.push('Missing conversion factor');
    } else { // Just some arbitrary checks here...
        if (uom_stock === null) {
          self.ValidationErrors.push('Einkaufseinheit muss definiert werden.');
        }
    }

    return self.ValidationErrors().length <= 0;
  };


  // Required for modal: Validate data
  self.ValidateInventoryItem4 = function(item) {
    if (!item) {
      return false;
    }

    var currentItem = ko.utils.unwrapObservable(item);
    var op_plan_date_start = ko.utils.unwrapObservable(currentItem.op_plan_date_start);
    var op_plan_date_end = ko.utils.unwrapObservable(currentItem.op_plan_date_end);
    var op_quantity_formatted = ko.utils.unwrapObservable(currentItem.op_quantity_formatted);

    self.ValidationErrors.removeAll(); // Clear out any previous errors

    if (op_quantity_formatted === null) {
      self.ValidationErrors.push('Bedarf muss 0 oder größer sein.');
    } else { // Just some arbitrary checks here...
        if (quantityBase < 0) {
          self.ValidationErrors.push('Bedarf muss 0 oder größer sein.');
        }
    }

    return self.ValidationErrors().length <= 0;
  };

  // Required for modal: Edit item in the modal window
  self.EditItem = function(item) {
    self.OriginalItemInstance(item);
    var now = new Date();
    var today = new Date(now.getFullYear(),now.getMonth(), now.getDate(), 0, 0, 0, 0); // returns current date in UTC
    var data = {
      'cp_type': item.cp_type(),
      'cp_quantity': item.cp_quantity(),
      'cp_period': item.cp_period(),
      'cp_quantity': item.cp_quantity(),
      'cp_plan_date_start': today,
      'cp_plan_date_end': default_plan_date_end
    };

    self.ItemBeingEdited(new InventoryItem(data));
  };

  // Required for modal: Edit item in the modal window
  self.EditItem2 = function(item) {

    self.OriginalItemInstance(item);

    var data = {
      'quantity_base': item.quantity_base(),
      'quantity_stock': item.quantity_stock()
    };

    self.ItemBeingEdited2(new InventoryItem(data));
  };

  // Required for modal: Edit item in the modal window
  self.EditItem3 = function(item) {
    self.OriginalItemInstance(item);
    var data = {
      'title': item.title(),
      'uom_stock': item.uom_stock(),
      'uom_base': item.uom_base(),
      'quantity_conversion_factor': item.quantity_conversion_factor()
    };
    self.ItemBeingEdited3(new InventoryItem(data));
  };

  // Required for modal: Edit item in the modal window
  self.EditItem4 = function(item) {
    self.OriginalItemInstance(item);
    var now = new Date();
    var today = new Date(now.getFullYear(),now.getMonth(), now.getDate(), 0, 0, 0, 0); // returns current date in UTC
    var data = {
      'op_plan_date_start': today,
      'op_plan_date_end': default_plan_date_end,
      'op_quantity': item.op_quantity()
    };
    self.ItemBeingEdited4(new InventoryItem(data));
  };


  // Save the changes back to the original instance in the collection.
  self.SaveItem = function() {
    var updatedItem = ko.utils.unwrapObservable(self.ItemBeingEdited);

    if (!self.ValidateInventoryItem(updatedItem)) {
      // Don't allow users to save items that aren't valid
      return false;
    }

    var cp_type = ko.utils.unwrapObservable(updatedItem.cp_type);
    var cp_quantity = ko.utils.unwrapObservable(updatedItem.cp_quantity);
    var cp_period = ko.utils.unwrapObservable(updatedItem.cp_period);
    var cp_weekday = ko.utils.unwrapObservable(updatedItem.cp_weekday);
    var cp_day_in_month = ko.utils.unwrapObservable(updatedItem.cp_day_in_month);
    var cp_plan_date_start = ko.utils.unwrapObservable(updatedItem.cp_plan_date_start);
    var cp_plan_date_end = ko.utils.unwrapObservable(updatedItem.cp_plan_date_end);

    if (self.OriginalItemInstance() === undefined) {
      return false;
    } else {
      // Updating an existing item
      self.OriginalItemInstance().suspend_backend_update(true);
      self.OriginalItemInstance().cp_type(cp_type);
      self.OriginalItemInstance().cp_quantity(cp_quantity);
      self.OriginalItemInstance().cp_period(cp_period);
      self.OriginalItemInstance().cp_weekday(cp_weekday);
      self.OriginalItemInstance().cp_day_in_month(cp_day_in_month);
      self.OriginalItemInstance().cp_plan_date_start(cp_plan_date_start);
      self.OriginalItemInstance().cp_plan_date_end(cp_plan_date_end);
      self.OriginalItemInstance().suspend_backend_update(false);
    }

    // Clear out any reference to a item being edited
    self.ItemBeingEdited(undefined);
    self.OriginalItemInstance(undefined);
  };

  // Save the changes back to the original instance in the collection.
  self.SaveItem2 = function() {
    var updatedItem = ko.utils.unwrapObservable(self.ItemBeingEdited2);
    if (!self.ValidateInventoryItem2(updatedItem)) {
      return false;
    }
    var quantity_base = ko.utils.unwrapObservable(updatedItem.quantity_base);
    var quantity_stock = ko.utils.unwrapObservable(updatedItem.quantity_stock);
    if (self.OriginalItemInstance() === undefined) {
      return false;
    } else {
      self.OriginalItemInstance().suspend_backend_update(true);
      self.OriginalItemInstance().quantity_base(quantity_base);
      self.OriginalItemInstance().quantity_stock(quantity_stock);
      self.OriginalItemInstance().quantity_base_user(quantity_base);
      self.OriginalItemInstance().quantity_stock_user(quantity_stock);
      self.OriginalItemInstance().suspend_backend_update(false);
    }
    self.ItemBeingEdited2(undefined);
    self.OriginalItemInstance(undefined);
  };

  // Save the changes back to the original instance in the collection.
  self.SaveItem3 = function() {
    var updatedItem = ko.utils.unwrapObservable(self.ItemBeingEdited3);
    if (!self.ValidateInventoryItem3(updatedItem)) {
      return false;
    }
    var title = ko.utils.unwrapObservable(updatedItem.title);
    var uom_base = ko.utils.unwrapObservable(updatedItem.uom_base);
    var uom_stock = ko.utils.unwrapObservable(updatedItem.uom_stock);
    var quantity_conversion_factor = ko.utils.unwrapObservable(updatedItem.quantity_conversion_factor);
    if (self.OriginalItemInstance() === undefined) {
      return false;
    } else {
      self.OriginalItemInstance().suspend_backend_update(true);
      self.OriginalItemInstance().title(title);
      self.OriginalItemInstance().uom_base(uom_base);
      self.OriginalItemInstance().uom_stock(uom_stock);
      self.OriginalItemInstance().quantity_conversion_factor(quantity_conversion_factor);
      self.OriginalItemInstance().suspend_backend_update(false);
    }
    self.ItemBeingEdited3(undefined);
    self.OriginalItemInstance(undefined);
  };

  // Save the changes back to the original instance in the collection.
  self.SaveItem4 = function() {
    var updatedItem = ko.utils.unwrapObservable(self.ItemBeingEdited4);
    if (!self.ValidateInventoryItem2(updatedItem)) {
      return false;
    }
    var op_plan_date_start = ko.utils.unwrapObservable(updatedItem.op_plan_date_start);
    var op_plan_date_end = ko.utils.unwrapObservable(updatedItem.op_plan_date_end);
    var op_quantity = ko.utils.unwrapObservable(updatedItem.op_quantity);

    if (self.OriginalItemInstance() === undefined) {
      return false;
    } else {
      self.OriginalItemInstance().suspend_backend_update(true);
      self.OriginalItemInstance().op_plan_date_start(op_plan_date_start);
      self.OriginalItemInstance().op_plan_date_end(op_plan_date_end);
      self.OriginalItemInstance().op_quantity(op_quantity);
      self.OriginalItemInstance().suspend_backend_update(false);
    }
    self.ItemBeingEdited4(undefined);
    self.OriginalItemInstance(undefined);
  };

  self.loadUnitsOfMeasure();
  self.loadInventoryItems();

}

var InventoryItem = function(data) {

  var formatter;
  var parser;
  formatter = localSetting.numberFormatter();
  parser = localSetting.numberParser();

  this.id = ko.observable(data.id);
  this.inventory_id = ko.observable(data.inventory_id);

  this.material_id = ko.observable(data.material);
  this.material_id.subscribe(saveInventoryItem, this);

  this.title = ko.observable(data.title);  // TODO: Enable multi-language support
  this.title.subscribe(saveInventoryItem, this);

  this.ignoreForecast = ko.observable(data.ignore_forecast);
  this.ignoreForecast.subscribe(saveInventoryItem, this);

  this.re_order_level = ko.observable(data.re_order_level);
  this.re_order_level.subscribe(saveInventoryItem, this);

  this.re_order_quantity = ko.observable(data.re_order_quantity);
  this.re_order_quantity.subscribe(saveInventoryItem, this);
  this.re_order_quantity_formatted = ko.pureComputed({
        read: function () {
          if (this.re_order_quantity() != null && typeof this.re_order_quantity() === 'number') {
            return formatter(this.re_order_quantity());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.re_order_quantity(value)
              }
            }
        },
        owner: this
    });

  this.suspend_backend_update = ko.observable(false);
  this.suspend_backend_update.subscribe(saveInventoryItem, this);

  this.uom_stock = ko.observable(data.uom_stock);
  this.uom_stock.subscribe(saveInventoryItem, this);

  this.uom_base = ko.observable(data.uom_base);
  this.uom_base.subscribe(saveInventoryItem, this);

  this.quantity_stock = ko.observable(data.quantity_stock);
  this.quantity_stock.subscribe(saveInventoryItem, this);
  this.quantity_stock_formatted = ko.pureComputed({
        read: function () {
          if (this.quantity_stock() != null && typeof this.quantity_stock() === 'number') {
            return formatter(this.quantity_stock());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.quantity_stock(value)
              }
            }
        },
        owner: this
    });

  this.quantity_stock_user = ko.observable(data.quantity_stock_user);

  this.quantity_base = ko.observable(data.quantity_base);
  this.quantity_base.subscribe(saveInventoryItem, this);
  this.quantity_base_formatted = ko.pureComputed({
        read: function () {
          if (this.quantity_base() != null && typeof this.quantity_base() === 'number') {
            return formatter(this.quantity_base());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.quantity_base(value)
              }
            }
        },
        owner: this
    });

  this.quantity_base_user = ko.observable(data.quantity_base_user);

  this.quantity_conversion_factor = ko.observable(data.quantity_conversion_factor);
  this.quantity_conversion_factor.subscribe(saveInventoryItem, this);
  this.quantity_conversion_factor_formatted = ko.pureComputed({
        read: function () {
          if (this.quantity_conversion_factor() != null && typeof this.quantity_conversion_factor() === 'number') {
            return formatter(this.quantity_conversion_factor());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.quantity_conversion_factor(value)
              }
            }
        },
        owner: this
    });

  this.cp_type = ko.observable(data.cp_type);
  this.cp_type.subscribe(saveInventoryItem, this);

  this.cp_quantity = ko.observable(data.cp_quantity);
  this.cp_quantity.subscribe(saveInventoryItem, this);
  this.cp_quantity_formatted = ko.pureComputed({
        read: function () {
          if (this.cp_quantity() != null && typeof this.cp_quantity() === 'number') {
            return formatter(this.cp_quantity());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.cp_quantity(value)
              }
            }
        },
        owner: this
    });

  this.cp_plan_date_start = ko.observable(data.cp_plan_date_start);
  this.cp_plan_date_start.subscribe(saveInventoryItem, this);

  this.cp_plan_date_end = ko.observable(data.cp_plan_date_end);
  this.cp_plan_date_end.subscribe(saveInventoryItem, this);

  this.cp_period = ko.observable(data.cp_period);
  this.cp_period.subscribe(saveInventoryItem, this);

  this.cp_weekday = ko.observable(data.cp_weekday);
  this.cp_weekday.subscribe(saveInventoryItem, this);

  this.cp_day_in_month = ko.observable(data.cp_day_in_month);
  this.cp_day_in_month.subscribe(saveInventoryItem, this);

  this.op_quantity = ko.observable(data.op_quantity);
  this.op_quantity.subscribe(saveInventoryItem, this);
  this.op_quantity_formatted = ko.pureComputed({
        read: function () {
          if (this.op_quantity() != null && typeof this.op_quantity() === 'number') {
            return formatter(this.op_quantity());
          }
        },
        write: function (value) {
            if (value != null && typeof value === 'string') {
              value = parser(value);
              if (!isNaN(value)) {
                this.op_quantity(value)
              }
            }
        },
        owner: this
    });

  this.op_plan_date_start = ko.observable(data.op_plan_date_start);
  this.op_plan_date_start.subscribe(saveInventoryItem, this);

  this.op_plan_date_end = ko.observable(data.op_plan_date_end);
  this.op_plan_date_end.subscribe(saveInventoryItem, this);

  this.forecasts = ko.observableArray(ko.utils.arrayMap(data.forecasts, function(forecast) {
    return new MaterialForecast(forecast);
  }));

  this.plannedQuantity = ko.computed( function() {
    var totalPlannedQuantity = 0;
    var d0_start = new Date(invVM.plan_date_start());
    var d0_end = new Date(invVM.plan_date_end());
    this.forecasts().forEach( function(element) {
      if (element.type() == 0) {
        var d1_start = new Date(element.plan_date_start());
        var d1_end = new Date(element.plan_date_end());
        var days = DaysOverlap(d0_start, d0_end, d1_start, d1_end);
        totalPlannedQuantity += days * element.quantity_per_day();
      }
    });
    return totalPlannedQuantity
  }, this);

  this.plannedQuantity_formatted = ko.pureComputed( function() {
    if (this.plannedQuantity() != null && typeof this.plannedQuantity() === 'number') {
      return formatter(this.plannedQuantity());
    }
  }, this);

  this.plannedQuantityOther = ko.computed( function() {
    var totalQuantity = 0;
    this.forecasts().forEach( function(element) {
      if (element.type() == 2) {
        //TODO: decide if quantity or quantity per day should be used
        totalQuantity += element.quantity();
      }
    });
    return totalQuantity
  }, this);

  this.plannedQuantityOther_formatted = ko.pureComputed( function() {
    if (this.plannedQuantityOther() != null && typeof this.plannedQuantityOther() === 'number') {
      return formatter(this.plannedQuantityOther());
    }
  }, this);

  this.plannedQuantityPeriodic = ko.computed( function() {
    var totalPlannedQuantity = 0;
    var d0_start = new Date(invVM.plan_date_start());
    var d0_end = new Date(invVM.plan_date_end());
    this.forecasts().forEach( function(element) {
      if (element.type() == 1) {
        var d1_start = new Date(element.plan_date_start());
        var d1_end = new Date(element.plan_date_end());
        var days = DaysOverlap(d0_start, d0_end, d1_start, d1_end);
        totalPlannedQuantity += days * element.quantity_per_day();
      }
    });
    return totalPlannedQuantity
  }, this);

  this.plannedQuantityPeriodic_formatted = ko.pureComputed( function() {
    if (this.plannedQuantityPeriodic() != null && typeof this.plannedQuantityPeriodic() === 'number') {
      return formatter(this.plannedQuantityPeriodic());
    }
  }, this);

  this.plannedQuantityTotal = ko.computed( function() {
    var totalQuantity = 0;
    totalQuantity = this.plannedQuantity() + this.plannedQuantityOther() + this.plannedQuantityPeriodic();
    return totalQuantity
  }, this);

  this.plannedQuantityTotal_formatted = ko.pureComputed( function() {
    if (this.plannedQuantityTotal() != null && typeof this.plannedQuantityTotal() === 'number') {
      return formatter(this.plannedQuantityTotal());
    }
  }, this);

  this.statusText = ko.observable();

  this.status = ko.computed(function() {
    if (this.plannedQuantityTotal() == 0 || this.ignoreForecast()) {
      this.statusText('zZ');
      return 0;
    } else if (this.plannedQuantityTotal() > 0 && this.quantity_base() == 0) {
      this.statusText('0%');
      return 1;
    } else if (this.quantity_base() < this.plannedQuantityTotal()) {
      this.statusText(Math.round(this.quantity_base() / this.plannedQuantityTotal()*100) + '%');
      return 2;
    } else if (this.quantity_base() >= this.plannedQuantityTotal()) {
      this.statusText(Math.round(this.quantity_base() / this.plannedQuantityTotal()*100) + '%');
      return 3;
    }
  }, this);

  this.statusClass = ko.computed(function() {
    switch (this.status()) {
      case 0: return 'no-need';
      case 1: return 'no-stock';
      case 2: return 'lack-stock';
      case 3: return 'on-stock';
    };
  }, this);

}

var MaterialForecast = function(data) {
  this.id = ko.observable(data.id);
  this.type = ko.observable(data.type);
  this.plan_date_start = ko.observable(data.plan_date_start);
  this.plan_date_end = ko.observable(data.plan_date_end);
  this.quantity_per_day = ko.observable(data.quantity_per_day);
  this.quantity = ko.observable(data.quantity);
  this.quantity_uom = ko.observable(data.quantity_uom);
}

var UnitOfMeasure = function(data) {
  this.uom = ko.observable(data.uom);
  this.type = ko.observable(data.type);
  this.longDE = ko.observable(data.longDE);
  this.longEN = ko.observable(data.longEN);
  this.shortDE = ko.observable(data.shortDE);
}

var dpVM = new dpViewModel();
ko.applyBindings(dpVM, document.getElementById('diet_plan'));

var invVM = new invViewModel();
ko.applyBindings(invVM, document.getElementById('inventory'));
