$(document).ready(function () {
  // if (pdata.stateData == undefined) {
  //   addListener(pdata, "stateData", {});
  // }
  // if (pdata.stateData.selected == undefined) {
  //   addListener(pdata.stateData, "selected", null);
  // }
  // if (pdata.stateData.selectedLinks == undefined) {
  //   addListener(pdata.stateData, "selectedLinks", null);
  // }
});
function getSelections() {
  message = {
    layout: $("#layouts").val(),
    nodecolors: $("#nodecolors").val(),
    links: $("#links").val(),
    linkcolors: $("#linkcolors").val(),
    main_tab: $("#tabs").tabs("option", "active"),
  };
  return message;
}

function updateSelection(data) {
  console.log(data);
  if (data.type == "node") {
    pdata["cbnode"] = data.selection;
  } else if (data.type == "link") {
    pdata["selectedLinks"] = data.selection;
  }
}

function addToSelection(id) {
  id = parseInt(id);
  if (
    (pdata.stateData.selected == null) |
    (pdata.stateData.selected == undefined)
  ) {
    pdata.stateData.selected = [];
  }
  if (!pdata.stateData.selected.includes(id)) {
    selected = pdata.stateData.selected;
    selected.push(id);
    pdata.stateData.selected = selected;
  }
}
function selectAnnotation(type, key, annotations) {
  var data = annotations[key];
  var dtype = data.dtype;
  var operator = null;
  var value = null;
  console.log(dtype);
  if ((dtype == "float") | (dtype == "int")) {
    value = $("#util_" + type + "_int").slider("option", "value");
    operator = $("#util_" + type + "_operator").slider("option", "value");
  } else if (dtype == "str") {
    value = $("#util_" + type + "_str").val();
  } else if ((dtype == "category") | (dtype == "bool")) {
    options = data.options;
    for (var i = 0; i < options.length; i++) {
      var radio = document.getElementById(
        "util_" + type + "_bool_" + options[i]
      );
      if (radio == null) {
        return;
      }
      if (radio.checked) {
        value = radio.value;
        break;
      }
    }
    if (value == null) {
      return;
    }
  }

  var key = clearOptions(key, type, true);
  var message = {
    dtype: dtype,
    value: value,
    annotation: key,
    type: type,
    operator: operator,
    project: sessionData["actPro"],
  };
  utilSocket.emit("select", message);
}
// Update selectmenu size
function updateDropDownClass(id) {
  $("#" + id).selectmenu({
    classes: {
      "ui-selectmenu-open": "twozerozero-open",
      "ui-selectmenu-button": "util-selection-limited-selectmenu-button",
    },
  });
  if (user_agent.includes("UnrealEngine")) {
    updateVRDropDownClass(id);
  }
}
// Update selectmenu font
function updateVRDropDownClass(id) {
  $("#" + id)
    .selectmenu("menuWidget")
    .menu({
      classes: {
        "ui-menu-item-wrapper": "limited-selectmenu-open-text",
      },
    });
}
// Update selectmenu options
function updateDropDown(parent, id, variable_id, annotation) {
  var options = Object.keys(annotation);
  if (options.length == 0) {
    document.getElementById(parent).style.visibility = "hidden";
    return;
  }
  document.getElementById(parent).style.visibility = "visible";
  var selectMenu = $("#" + id);
  // clear the current options
  selectMenu.empty();
  // define the list of options
  // append new options to the selectmenu
  $.each(options, function (index, option) {
    selectMenu.append($("#" + id).append(new Option(option)));
  });
  var key = $("#" + id).val();
  initVariables(key, variable_id, annotation);
  // refresh the selectmenu to update its style
  selectMenu.selectmenu("refresh");
}
function initVariables(key, variable_id, annotation) {
  var data = annotation[key];
  var dtype = data.dtype;
  var space = document.getElementById(variable_id);
  var type = "node";
  if (variable_id.includes("link")) {
    type = "link";
  }

  if ((dtype == "float") | (dtype == "int")) {
    utilHandleNumericVariable(data, key, dtype, space, type);
  } else if (dtype == "str") {
    utilHandleStringVariable(data, space, type);
  } else if ((dtype == "bool") | (dtype == "category")) {
    untilHandleBoolVariable(data, space, type);
  }
}

function clearOptions(option, type, reverse = false) {
  var replaceMap = {
    s: "Source Node",
    e: "Sink Node",
    n: "Name",
    id: type.charAt(0).toUpperCase() + type.slice(1) + " Identifier",
  };
  var to_check = Object.keys(replaceMap);
  if (reverse) {
    var tmp = replaceMap;
    replaceMap = {};
    for (var key in tmp) {
      replaceMap[tmp[key]] = key;
    }
    to_check = Object.keys(replaceMap);
  }
  if (to_check.includes(option)) {
    option = replaceMap[option];
  }

  return option;
}
function utilHandleNumericVariable(data, key, dtype, space, type) {
  var special = false;
  var operator_middle = 2;
  if (["Source Node", "Sink Node", "Name"].includes(key)) {
    special = true;
    operator_middle = 1;
  }

  var max = data.max;
  var min = data.min;
  if (min >= 0) {
    min = 0;
  }
  var middle = (max + min) / 2;
  var step = 1;
  if (dtype == "float") {
    step = 0.001;
    max = Number(max.toFixed(2));
    min = Number(min.toFixed(2));
    middle = Number(middle.toFixed(2));
    if (max < 1) {
      max = 1;
    }
  } else {
    max = Math.round(max);
    min = Math.round(min);
    middle = Math.round(middle);
  }

  slider_container = document.createElement("div");
  slider_container.classList.add("frameBox");
  slider_container.style =
    "display: flex;align-items: center;padding:0px;margin-top:-10px;max-height:40px;";
  slider_container.id = "util_" + type + "_slider_container";

  // Operator
  operator_container = document.createElement("div");
  operator_container.style = "width:100%;padding:0px;margin-top;";
  operator_container.id = "util_" + type + "_operator_container";

  slider_block = document.createElement("div");
  slider_block.style =
    "width:100%;padding:0px;padding-bottom:10px;margin-bottom:0px;";
  operator_slider = document.createElement("div");
  operator_slider.style =
    "width:60%;margin-left:20%;,margin-right:20%;margin-bottom:0px";
  operator_slider.id = "util_" + type + "_operator";
  slider_block.appendChild(operator_slider);

  symbol_block = document.createElement("div");
  symbol_block.style = "width:100%;padding:0px;margin-bottom:0px;";
  symbol_block.id = "util_" + type + "_symbol_block";

  button_style =
    "width:30%;padding:0px;height:30px !important;border-width:2px;margin-top:0px;margin-bottom:0px;";
  smaller = document.createElement("input");
  smaller.type = "button";
  smaller.value = "≤";
  smaller.id = "util_" + type + "_smaller";
  smaller.style = button_style;
  equal = document.createElement("input");
  equal.type = "button";
  equal.value = "=";
  equal.id = "util_" + type + "_smaller";
  equal.style = button_style;
  larger = document.createElement("input");
  larger.type = "button";
  larger.value = "≥";
  larger.id = "util_" + type + "_larger";
  larger.style = button_style;
  symbol_block.appendChild(smaller);
  symbol_block.appendChild(equal);
  symbol_block.appendChild(larger);

  operator_container.appendChild(slider_block);
  operator_container.appendChild(symbol_block);

  // Silder
  slider = document.createElement("div");
  slider.id = "util_" + type + "_int";
  slider.style = "width: 60%;";

  // Value representing slider value
  value = document.createElement("p");
  value.id = "util_" + type + "_int_value";
  value.style = "margin-left:5%;white-space: nowrap;overflow: hidden;width:35%";

  slider_container.appendChild(slider);

  if (special && data.values) {
    value.innerHTML = data.values[middle];
  } else {
    value.innerHTML = middle;
  }
  slider_container.appendChild(value);

  space.innerHTML = "<p></p>";
  space.classList.add("frameBox");
  space.appendChild(slider_container);
  space.appendChild(operator_container);

  if (special && data.values) {
    kwargs = { type: type, values: data.values, value_id: value.id };
    func = function (ui, { type: type, value_id: value_id, values: values }) {
      $("#" + value_id).text(values[ui.value]);
    };
  } else {
    kwargs = { type: type, value_id: value.id };
    func = function (ui, { type: type, value_id: value_id }) {
      $("#" + value_id).text(ui.value);
    };
  }
  utilVariableSlider(slider.id, min, max, middle, step, func, kwargs);
  utilVariableSlider(
    operator_slider.id,
    (min = 0),
    (max = 2),
    (middle = operator_middle),
    (step = 1)
  );
  if (special) {
    document.getElementById(operator_container.id).style.visibility = "hidden";
  }
}
function utilVariableSlider(id, min, max, middle, step, func, kwargs = {}) {
  $("#" + id).slider({
    animate: true,
    range: "max",
    min: min,
    max: max,
    value: middle,
    step: step,
    slide: function (event, ui) {
      if (func != undefined) {
        func(ui, kwargs);
      }
    },
    stop: function (event, ui) {
      socket.emit("ex", {
        id: id,
        val: ui.value,
        fn: "sli",
      });
    },
  });
}

function utilHandleStringVariable(data, space, type) {
  var options = data.options;
  drop_down = document.createElement("select");
  drop_down.id = "util_" + type + "_str";
  space.innerHTML = "<p></p>";
  space.appendChild(drop_down);
  initDropdown(drop_down.id, options, options[0]);
  updateDropDownClass(drop_down.id);
}
function untilHandleBoolVariable(data, space, type) {
  var options = data.options;
  option_div = document.createElement("div");
  option_div.id = "util_" + type + "_bool";
  option_div.style = "display:block;justify-content: space-between;";
  list = document.createElement("ul");
  list.id = "util_" + type + "_bool_list";
  list.classList.add("util-bool-list");
  for (var i = 0; i < options.length; i++) {
    option = options[i];
    list_item = document.createElement("li");
    list_item.style = "flex:" + 1 / options.length + ";";
    var option_radio = document.createElement("input");
    var label_div = document.createElement("label");
    label_div.innerHTML = option;
    label_div.htmlFor = "util_" + type + "_bool_" + option;
    option_radio.type = "radio";
    option_radio.value = option;
    option_radio.id = "util_" + type + "_bool_" + option;
    option_radio.name = "util_" + type + "_bool";

    list_item.appendChild(option_radio);
    list_item.appendChild(label_div);
    list.appendChild(list_item);
  }
  option_div.appendChild(list);
  space.innerHTML = "<p></p>";
  space.appendChild(option_div);
  if (options.length == 1) {
    var radio = document.getElementById("util_" + type + "_bool_" + options[0]);
    radio.checked = true;
    radio.disabled = true;
  }
}
// Reset project, selected nodes or selected links
function resetSelection(id, type, sm) {
  var message = {
    id: id,
    type: type,
    selection: null,
    sm: sm,
    text: $(document.getElementById(id)).val(),
  };
  console.log(message);
  utilSocket.emit("reset", message);
  updateSelection(message);
}
function updateProjectList(projectName) {
  if (sessionData.proj.includes(projectName)) {
    return;
  }
  sessionData.proj.push(projectName);
  $("#projects").append(new Option(projectName));
  $("#projects").selectmenu("refresh");
}

function initExtDropdown(data) {
  console.log("init dropdown", data.id);
  var element = document.getElementById(data.id);
  if (element) {
    var select = element.shadowRoot.getElementById("sel");
    var count = element.shadowRoot.querySelector("#count");
    var content = element.shadowRoot.getElementById("content");
    var socketDomain = element.getAttribute("socketDomain");
    if (data.hasOwnProperty("opt")) {
      removeAllChildNodes(content);
      cmul = 70;
      //.log(data.opt.length)
      for (let i = 0; i < data.opt.length; i++) {
        $(content).append(
          "<ext-button id = 'button" +
            i +
            " 'val= '" +
            i +
            "' name = '" +
            data.opt[i] +
            "'socketDomain= '" +
            socketDomain +
            "' width = '375px' parent = '" +
            data.parent +
            "' fn = 'dropdown' color = '" +
            rgbToHex(
              Math.floor(Math.random() * cmul),
              Math.floor(Math.random() * cmul),
              Math.floor(Math.random() * cmul)
            ) +
            "' ></mc-button>"
        );
      }
      select.value = data.opt[data.sel];
      count.innerHTML = " [" + data.opt.length + "]";
      content.style.display = "none";
    } else {
      //this comes from the buttons
      select.value = data.name;
      content.style.display = "none";
    }
  }
}
