
// Returns the ISO week of the date.
// source: https://weeknumber.net/how-to/javascript
DateGetWeek = function(d) {
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
var ViewModel = function() {
  var self = this;

  self.meals = ko.observableArray([]);
  self.week_selected = ko.observable('');
  self.week_range = ko.observableArray([]);
  self.timeGrid = ko.observableArray([]);

  self.loadMeals = function() {
    $.ajax({
      type: 'GET',
      url: url_api_meals,
      dataType: 'json',
      success: function(response) {
        // turn the json string into a javascript object
        var parsed = response['meals']

        // for each iterable item create a new DietPlanItem observable
        parsed.forEach( function(item) {
          self.meals.push( new Meal(item) );
        });
      }
    });
  }

  self.changeWeek = function(data, event) {
    self.week_selected(data.week_number());
  }


//TODO: Finish the init part to separate initialization from change week selector
  self.initGrid = function() {
    var start_date = new Date();
    const week_range_max = 3;
    const num_days = 7;

    // Determine date of first day of the current week
    var today_weekday = (start_date.getDay() + 6) % 7; // monday is fist not sunday
    d.setDate(start_date.getDate() - today_weekday);

    // Set current week as selected
    self.week_selected(DateGetWeek(d));

    // Determine week number range
    var d2 = new Date(d.getTime());
    item = {
      week_number: DateGetWeek(d2),
      date_first_day: d2.getTime()
    }
    self.week_range.push( new GridWeek(item) );
    for (var i = 1; i < week_range_max; i++) {
      d2.setDate(d2.getDate() + 7);
      item = {
        week_number: DateGetWeek(d2),
        date_first_day: d2.getTime()
      }
      console.log('Date beginning of week = ' + d2.toLocaleDateString());
      self.week_range.push( new GridWeek(item) );
    }

  }


  self.setViewPeriod = function(start_date) {

    self.timeGrid.removeAll();
    var date_range = [];
    var item = '';
    var d_string = '';
    var d = new Date();
    const week_range_max = 3;
    const num_days = 7;

    // If no start_date defined then set current date
    if (!start_date) {
      var start_date = new Date();
    }

    // Determine date of first day of the current week
    var today_weekday = (start_date.getDay() + 6) % 7; // monday is fist not sunday
    d.setDate(start_date.getDate() - today_weekday);
    console.log('First day of the week = ' + d.toLocaleDateString());

    // Set current week as selected
    self.week_selected(DateGetWeek(d));
    console.log('Current week = ' + self.week_selected());

    // Determine week number range
    var d2 = new Date(d.getTime());
    item = {
      week_number: DateGetWeek(d2),
      date_first_day: d2.getTime()
    }
    self.week_range.push( new GridWeek(item) );
    for (var i = 1; i < week_range_max; i++) {
      d2.setDate(d2.getDate() + 7);
      item = {
        week_number: DateGetWeek(d2),
        date_first_day: d2.getTime()
      }
      console.log('Date beginning of week = ' + d2.toLocaleDateString());
      self.week_range.push( new GridWeek(item) );
    }

    // Determine current week date range
    d.setDate(d.getDate() - 1);
    for (var i = 0; i < num_days; i++) {
      d.setDate(d.getDate() + 1);
      d_string = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
      date_range.push(d_string);
    }

    // Create a timeGrid for each day in the range
    date_range.forEach( function(item) {

      // add a day into the timeGrid
      // TODO: Turn timeGrid into GridWeek (merge)
      var grid_day = new GridDay(item);
      self.timeGrid.push( grid_day )

      $.ajax({
        type: 'GET',
        url: url_dp_details,
        dataType: 'json',
        data: {
          'plan_date' : item
        },
        success: function(response) {

          // turn the json string into a javascript object
          var parsed = response['diet_plan_items'] // JSON.parse(response['diet_plan_items']);

          // for each iterable item create a new DietPlanItem observable
          parsed.forEach( function(item) {
            grid_day.dietPlanItems.push( new DietPlanItem(item) );
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
  self.setViewPeriod();
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

var GridDay = function(data) {
  this.date = ko.observable(data);
  this.dayShort = ko.pureComputed(function() {
    var d = new Date(this.date());
    return d.toDateString()
  }, this);
  this.dietPlanItems = ko.observableArray([]);
  this.meal_id_select2add = ko.observable();
}

var GridWeek = function(data) {
  this.week_number = ko.observable(data.week_number);
  this.date_first_day = ko.observable(data.date_first_day);
}

var vm = new ViewModel();
ko.applyBindings(vm);
