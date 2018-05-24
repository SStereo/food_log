"use strict";
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
    var itemValue = '';
    var itemId = '';
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
    var today = new Date();
    var d = new Date();
    const week_range_max = 3;
    const num_days = 7;

    // Determine date of first day of the current week
    var today_weekday = (today.getDay() + 6) % 7; // monday is fist not sunday
    d.setDate(today.getDate() - today_weekday);

    // Make first week the default selected one
    self.weekSelected(0);  // TODO: Find a better way for filtering

    // ++++++ Generate Week Objects +++++
    var d2 = new Date(d.getTime());
    var d3 = new Date();
    for (var i = 0; i < week_range_max; i++) {
      date_range = [];
      // after the first week increment the start day by 7 days
      if (i > 0) {
        d2.setDate(d2.getDate() + 7);
      }

      // Copy start date into other variable
      d3 = new Date(d2.getTime());

      // Determine all days of week
      d3.setDate(d3.getDate() - 1);
      for (var y = 0; y < num_days; y++) {
        d3.setDate(d3.getDate() + 1);
        d_string = d3.getFullYear() + '-' + (d3.getMonth() + 1) + '-' + d3.getDate();
        date_range.push(d_string);
      }

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
      // Loads data from the REST API
      $.ajax({
        type: 'GET',
        url: url_api_dietplan,
        dataType: 'json',
        data: {
          'plan_date' : item.date()
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

    $.ajax({
      type: 'DELETE',
      url: url_api_dietplan,
      dataType: 'json',
      data: {
        'id' : data.id(),
        'diet_plan_id' : dp_id,
        'meal_id' : data.meal_id(),
        'plan_date' : data.plan_date(),
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

    console.log('addDietPlanItem(meal_id=' + data.meal_id_select2add() + ')');

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
        'plan_date' : data.date(),
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
  console.log('saveDietPlanItem: newValue = ' + newValue + ', id = ' + this.id());

  $.ajax({
    type: 'PUT',
    url: url_api_dietplan,
    dataType: 'json',
    data: {
      'id' : this.id(),
      'diet_plan_id' : dp_id,
      'meal_id' : this.meal_id(),
      'plan_date' : this.plan_date(),
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

// Custom binding for a modal bootstrap

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


function saveInventoryItem(newValue) {
  $.ajax({
    type: 'PUT',
    url: url_api_inventory,
    dataType: 'json',
    data: {
      'id' : this.id(),
      'inventory_id' : inv_id,
      'titleEN' : this.titleEN(),
      'titleDE' : this.title(),
      'status' : this.status(),
      'material_id' : this.material_id(),
      'level' : this.level(),
      're_order_level' : this.re_order_level(),
      're_order_quantity' : this.re_order_quantity()
    },
    headers: {
      'X-CSRFTOKEN' : csrf_token
    },
    success: function(response) {
      //TODO: undo changes in case of failure
      console.log('saveInventoryItem: success');
    }
  });
}


var invViewModel = function() {
  var self = this;
  this.inventoryItems = ko.observableArray([]);
  const default_forecast_days = 7;
  this.planForecastDays = ko.observable(default_forecast_days);

  // TODO: Avoid start date contains h:m:s
  this.plan_date_start = ko.observable( new Date() );
  this.plan_date_end = ko.computed( function() {
    var dateTo = new Date(self.plan_date_start()); //new Date();
    dateTo.setDate(dateTo.getDate() + parseInt(self.planForecastDays()));
    return dateTo;
  } );

  // store the new Inventory value being entered
	this.current = ko.observable();
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
  self.loadInventoryItems = function() {
    self.inventoryItems.removeAll();
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
    console.log('toggle');
    if (data.status() < 3) {
      data.status(data.status() + 1);
    } else {
      data.status(0);
    }
  };

  // adds a inventory item
  self.addInventoryItem = function(data, event) {

    var current = self.current().trim();
    if (current) {
      console.log('addInventoryItem');

      $.ajax({
        type: 'POST',
        url: url_api_inventory,
        headers: {
          'X-CSRFTOKEN' : csrf_token
        },
        dataType: 'json',
        data: {
          'titleEN' : '',
          'titleDE' : current,
          'status' : 1,
        },
        success: function(response) {

          // turn the json string into a javascript object
          var parsed = response['inventory_item']

          // for each iterable item create a new DietPlanItem observable
          parsed.forEach( function(item) {
            self.inventoryItems.push( new InventoryItem(item) );
          });
        }
      });
    }
    self.current('');
  };

  // edit an item
	this.editItemOld = function (item) {
		item.editing(true);
		item.previousTitle = item.title();
	}.bind(this);

  // stop editing an item.  Remove the item, if it is now empty
	this.saveEditing = function (item) {
		item.editing(false);

		var title = item.title();
		var trimmedTitle = title.trim();

		// Observable value changes are not triggered if they're consisting of whitespaces only
		// Therefore we've to compare untrimmed version with a trimmed one to chech whether anything changed
		// And if yes, we've to set the new value manually
		if (title !== trimmedTitle) {
			item.title(trimmedTitle);
		}

		if (!trimmedTitle) {
			this.remove(item);
		}
	}.bind(this);

	// cancel editing an item and revert to the previous content
	this.cancelEditing = function (item) {
		item.editing(false);
		item.title(item.previousTitle);
	}.bind(this);

  // Required for modal: Validate data
  self.ValidateInventoryItem = function(item) {
    if (!item) {
      return false;
    }

    var currentItem = ko.utils.unwrapObservable(item);
    var currentLevel = ko.utils.unwrapObservable(currentItem.level);
    var currentTitle = ko.utils.unwrapObservable(currentItem.title);
    var currentReOrderLevel = ko.utils.unwrapObservable(currentItem.re_order_level);

    self.ValidationErrors.removeAll(); // Clear out any previous errors

    if (!currentLevel) {
      self.ValidationErrors.push("Stock level is required.");
    } else { // Just some arbitrary checks here...
      if (Number(currentLevel) == currentLevel && currentLevel % 1 === 0) { // is a whole number
        if (currentLevel < 0) {
          self.ValidationErrors.push("The stock level must be zero or greater.");
        }
      } else {
        self.ValidationErrors.push("Please enter a valid whole number for the stock level.");
      }
    }

    if (!currentTitle) {
      self.ValidationErrors.push("Please enter a title for the item");
    }

    return self.ValidationErrors().length <= 0;
  };

  // Required for modal: The instance of the item currently being edited.
  self.ItemBeingEdited = ko.observable();

  // Required for modal: Used to keep a reference back to the original user record being edited
  self.OriginalItemInstance = ko.observable();

  // Required for modal: add new item, TODO: combine with existing approach
  self.AddNewItem = function() {
    // Load up a new user instance to be edited
    self.ItemBeingEdited(new InventoryItem());
    self.OriginalItemInstance(undefined);
  };

  // Required for modal: Edit item in the modal window
  self.EditItem = function(item) {
    // Keep a copy of the original instance so we don't modify it's values in the editor
    self.OriginalItemInstance(item);
    console.log('click');
    // Copy the user data into a new instance for editing. TODO: this does not work

    var data = {
      'titleDE': item.title(),
      'level': item.level(),
      're_order_quantity': item.re_order_quantity()
    }

    self.ItemBeingEdited(new InventoryItem(data));
  };

  // Save the changes back to the original instance in the collection.
  self.SaveItem = function() {
    var updatedItem = ko.utils.unwrapObservable(self.ItemBeingEdited);

    if (!self.ValidateInventoryItem(updatedItem)) {
      // Don't allow users to save items that aren't valid
      return false;
    }

    var itemTitle = ko.utils.unwrapObservable(updatedItem.title);
    var itemLevel = ko.utils.unwrapObservable(updatedItem.level);
    var itemReOrderLevel = ko.utils.unwrapObservable(updatedItem.re_order_level);

    if (self.OriginalItemInstance() === undefined) {
      return false;
    } else {
      // Updating an existing user
      self.OriginalItemInstance().title(itemTitle);
      self.OriginalItemInstance().level(itemLevel);
      self.OriginalItemInstance().re_order_level(itemReOrderLevel);
    }

    // Clear out any reference to a user being edited
    self.ItemBeingEdited(undefined);
    self.OriginalItemInstance(undefined);
  };


  self.loadInventoryItems();

}

var InventoryItem = function(data) {
  this.id = ko.observable(data.id);
  this.inventory_id = ko.observable(data.inventory_id);

  this.title = ko.observable(data.titleDE);  // TODO: Enable multi-language support
  this.title.subscribe(saveInventoryItem, this);

  this.titleEN = ko.observable(data.titleEN);  // TODO: Enable multi-language support
  this.titleEN.subscribe(saveInventoryItem, this);

  this.level = ko.observable(data.level);
  this.level.subscribe(saveInventoryItem, this);

  this.ignoreForecast = ko.observable(data.ignoreForecast);
  this.ignoreForecast.subscribe(saveInventoryItem, this);

  this.consumed = ko.observable(data.consumed);
  this.consumed.subscribe(saveInventoryItem, this);

  this.need_additional = ko.observable(data.need_additional);
  this.need_additional.subscribe(saveInventoryItem, this);

  this.re_order_level = ko.observable(data.re_order_level);
  this.re_order_level.subscribe(saveInventoryItem, this);

  this.re_order_quantity = ko.observable(data.re_order_quantity);
  this.re_order_quantity.subscribe(saveInventoryItem, this);

  this.material_id = ko.observable(data.material);
  this.material_id.subscribe(saveInventoryItem, this);

  this.editing = ko.observable(false);

  this.uom = ko.observable(data.uom);
  this.uom.subscribe(saveInventoryItem, this);

  this.forecasts = ko.observableArray(ko.utils.arrayMap(data.forecasts, function(forecast) {
    return new MaterialForecast(forecast);
  }));

  this.plannedQuantity = ko.computed( function() {
    var totalPlannedQuantity = 0;
    var d1 = new Date(invVM.plan_date_start());
    var d2 = new Date(invVM.plan_date_end());
    this.forecasts().forEach( function(element) {
      var planDate = new Date(element.plan_date());
      if (planDate >= d1 && planDate <= d2) {
        totalPlannedQuantity += element.quantity();
      }
    });
    return totalPlannedQuantity
  }, this);

  this.status = ko.computed(function() {
    if (this.plannedQuantity() == 0 || this.ignoreForecast()) {
      return 0;
    } else if (this.plannedQuantity() > 0 && this.level() == 0) {
      return 1;
    } else if (this.level() < this.plannedQuantity()) {
      return 2;
    } else if (this.level() >= this.plannedQuantity()) {
      return 3;
    }
  }, this);

  this.statusText = ko.computed(function() {
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
  this.plan_date = ko.observable(data.plan_date);
  this.quantity = ko.observable(data.quantity);
  this.quantity_uom = ko.observable(data.quantity_uom);
}


var dpVM = new dpViewModel();
ko.applyBindings(dpVM, document.getElementById('diet_plan'));

var invVM = new invViewModel();
ko.applyBindings(invVM, document.getElementById('inventory'));
