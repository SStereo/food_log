
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
