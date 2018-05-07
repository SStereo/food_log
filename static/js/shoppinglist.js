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
  self.week_selected = ko.observable('');
  self.week_range = ko.observableArray([]);

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

  self.changeWeek = function(data, event) {
    self.week_selected(data.week_index());
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
    self.week_selected(0);  // TODO: Find a better way for filtering

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
      self.week_range.push(grid_week);

      // Create GridDay objects for each day in the date range
      grid_week.date_range().forEach( function(item) {
        var grid_day = new GridDay(item);
        grid_week.grid_days.push( grid_day )
      })

    }
    // +++++++++++++++++++++++
  }

  self.loadDietPlanItems = function() {
    var index = self.week_selected();
    self.week_range()[index].grid_days().forEach( function(item) {
      // Deletes all dietPlanObjects prior of loading them fresh from the server
      item.dietPlanItems.removeAll();
      // Loads data from the REST API
      $.ajax({
        type: 'GET',
        url: url_dp_details,
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
      url: url_dp_details,
      dataType: 'json',
      data: {
        'id' : data.id(),
        'diet_plan_id' : dp_id,
        'meal_id' : data.meal_id(),
        'plan_date' : data.plan_date(),
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
      url: url_dp_details,
      headers: {
        'X-CSRF-TOKEN' : csrf_token
      },
      dataType: 'json',
      data: {
        'diet_plan_id' : dp_id,
        'meal_id' : data.meal_id_select2add(),
        'plan_date' : data.date(),
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
  self.loadMeals();
  self.initGrid();
  self.loadDietPlanItems();

  self.selectedGridWeek = ko.computed(function() {
    // Sets the selected week by filtering on the index
    var index = self.week_selected();
    return ko.utils.arrayFilter(self.week_range()[index].grid_days(), function(item) {
      return true;
    });

    // TODO: This is NOT WORKING
    var array = ko.utils.arrayFilter(self.week_range(), function(item) {
      if (item.week_number() == self.week_selected()) {
        return true;
      } else {
        return false;
      }
    });
    return array.grid_days;

  })

}

//TODO: this is the only CRUD function sitting outside of the ViewModel -> fix
function saveDietPlanItem(newValue) {
  console.log('saveDietPlanItem: newValue = ' + newValue + ', id = ' + this.id());

  $.ajax({
    type: 'PUT',
    url: url_dp_details,
    dataType: 'json',
    data: {
      'id' : this.id(),
      'diet_plan_id' : dp_id,
      'meal_id' : this.meal_id(),
      'plan_date' : this.plan_date(),
      'consumed' : this.consumed(),
      'portions' : this.portions()
    },
    success: function(response) {
      //TODO: undo changes in case of failure
      console.log('saveDietPlanItem: success');
    }
  });

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

var invViewModel = function() {
  var self = this;

}

var dpVM = new dpViewModel();
ko.applyBindings(dpVM, document.getElementById('diet_plan'));
