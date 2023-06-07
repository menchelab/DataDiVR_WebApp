let nodeAnnotations = new VariableListener({
  selectedAnnotation: 0,
  annotationKeys: [],
});
let linkAnnotations = new VariableListener({
  selectedAnnotation: 0,
  annotationKeys: [],
});
$(document).ready(function () {
  document.getElementById("util_node_annot").style.visibility = "hidden";
  document.getElementById("util_link_annot").style.visibility = "hidden";
  if (pfile == undefined) {
    pfile = new VariableListener({ name: "" });
  }
  if (pfile.name == undefined) {
    pfile.addListener("name", "");
  }
  pfile.nameRegisterListener(function (val) {
    console.log(
      "NAME CHANGED TO " + pfile["name"] + " WILL ASK FOR ANNOTATION"
    );
    utilSocket.emit("annotation", { type: "node", project: pfile.name });
    utilSocket.emit("annotation", { type: "link", project: pfile.name });
  });
  // setTimeout(function () {
  //   utilSocket.emit("getSelection");
  // }, 1000);
  if (pdata == undefined) {
    pdata = new VariableListener({ cbnode: [], selectedLinks: [] });
  }

  // Display number of selected Nodes
  if (pdata.cbnode == undefined) {
    pdata.addListener("cbnode", []);
  }

  var nodeSelectCounter = document.getElementById("util_node_selection_count");
  pdata.cbnodeRegisterListener(function (val) {
    nodeSelectCounter.innerHTML = val.length;
  });
  var selectNodes = document.getElementById("util_node_selection_select");
  var selectNodes = selectNodes.shadowRoot.querySelector("#name");
  selectNodes.addEventListener("click", function () {
    annotationKey = nodeAnnotations["selectedAnnotation"];
    annotation = nodeAnnotations["annotationKeys"][annotationKey];
    dtype = nodeAnnotations[annotation]["dtype"];
    var value = "";
    var operator = "";
    if (["float", "int"].includes(dtype)) {
      value = new Number(
        document
          .getElementById("util_node_numeric_slider")
          .shadowRoot.querySelector("#myRange").value
      );
      operator = new Number(
        document
          .getElementById("util_node_logic_slider")
          .shadowRoot.querySelector("#myRange").value
      );
    } else {
      value = document
        .getElementById("util_nodeAnnoDD")
        .shadowRoot.querySelector("#sel").value;
    }
    var message = {
      annotation: annotation,
      type: "node",
      dtype: dtype,
      value: value,
      operator: operator,
    };
    utilSocket.emit("select", message);
  });

  // Display number of selected Links
  if (pdata.selectedLinks == undefined) {
    pdata.addListener("selectedLinks", []);
  }

  var linkSelectCounter = document.getElementById("util_link_selection_count");
  pdata.selectedLinksRegisterListener(function (val) {
    linkSelectCounter.innerHTML = val.length;
  });
  var selectedLinks = document.getElementById("util_link_selection_select");
  var selectedLinks = selectedLinks.shadowRoot.querySelector("#name");
  selectedLinks.addEventListener("click", function () {
    annotationKey = linkAnnotations["selectedAnnotation"];
    annotation = linkAnnotations["annotationKeys"][annotationKey];
    dtype = linkAnnotations[annotation]["dtype"];
    var value = "";
    var operator = "";
    if (["float", "int"].includes(dtype)) {
      value = new Number(
        document
          .getElementById("util_link_numeric_slider")
          .shadowRoot.querySelector("#myRange").value
      );
      operator = new Number(
        document
          .getElementById("util_link_logic_slider")
          .shadowRoot.querySelector("#myRange").value
      );
    } else {
      value = document
        .getElementById("util_linkAnnoDD")
        .shadowRoot.querySelector("#sel").value;
    }
    var message = {
      annotation: annotation,
      type: "link",
      dtype: dtype,
      value: value,
      operator: operator,
    };
    utilSocket.emit("select", message);
  });

  // setSelectionNumber("util_num_nodes")(pdata.cbnode);
  // setSelectionNumber("util_num_links")(pdata.selectedLinks);
  // Node selection listener
  // pdata.cbnodeRegisterListener(setSelectionNumber("util_num_nodes"));
  // // Link selection listener
  // pdata.selectedLinksRegisterListener(setSelectionNumber("util_num_links"));
});
function updateAnnoDD(data) {
  var annotListener = undefined;
  var ddId = undefined;
  var numericId = undefined;
  var sliderId = undefined;

  if (data.type == "node") {
    annotListener = nodeAnnotations;
    ddId = "util_nodeAnnoDD";
    numericId = "util_node_numeric_logic";
    sliderId = "util_node_numeric_slider";
  } else {
    annotListener = linkAnnotations;
    ddId = "util_linkAnnoDD";
    numericId = "util_link_numeric_logic";
    sliderId = "util_link_numeric_slider";
  }
  var ddIndex = annotListener["selectedAnnotation"];
  if (ddIndex == null || ddIndex == "") {
    ddIndex = 0;
  }
  var selectedKey = annotListener["annotationKeys"][ddIndex];
  var annotation = annotListener[selectedKey];

  console.log("UPDATE ANNOTDD");
  console.log(annotationKeys);
  console.log(ddIndex);
  console.log(selectedKey);
  console.log(annotation);

  var dataType = annotation["dtype"];
  if (["float", "int"].includes(dataType)) {
    handleNumericAnnoation(ddId, numericId, sliderId, annotation, dataType);
  } else {
    handleNonNumericAnnoation(ddId, numericId, annotation);
  }
}
function handleNumericAnnoation(
  ddId,
  numericId,
  sliderId,
  annotation,
  dataType
) {
  var dd = document.getElementById(ddId);
  dd.style.display = "none";
  var numeric = document.getElementById(numericId);
  numeric.style.display = "block";
  var slider_div = document.getElementById(sliderId);
  var slider = slider_div.shadowRoot.querySelector("#myRange");
  var value = slider_div.shadowRoot.querySelector("#value");
  if (dataType == "float") {
    slider.step = 0.01;
  } else {
    slider.step = 1;
  }
  slider.min = annotation["min"];
  slider.max = annotation["max"];
  slider.value = (annotation["max"] - annotation["min"]) / 2;
  value.textContent = slider.value;
  console.log("changed numeric slider to:");
  console.log(slider);
  console.log((annotation["max"] - annotation["min"]) / 2);
  console.log(slider.value);
}
function handleNonNumericAnnoation(ddId, numericId, annotation) {
  console.log("not numeric");
  // Show the annotation dropdown
  var dd = document.getElementById(ddId);
  dd.style.display = "block";
  annotData = {
    id: ddId,
    opt: annotation["options"],
    sel: 0,
    parent: ddId,
  };
  initExtDropdown(annotData);

  // Hide the numeric slider
  var numeric = document.getElementById(numericId);
  numeric.style.display = "none";
}
function updatedAnnotations(data) {
  annotationKeys = Object.keys(data.annotations);
  console.log("updated annotations");
  var ddIndex = 0;
  var annotDiv = "";
  if (data.selectedAnnot != null) {
    ddIndex = annotationKeys.indexOf(data.selectedAnnot);
    if (ddIndex == -1) {
      ddIndex = 0;
    }
  }
  console.log("ddIndex");
  console.log(ddIndex);
  if (data.type == "node") {
    annotDiv = "util_node_annot";
    ddId = "util_nodeDD";
    annotData = {
      id: ddId,
      opt: annotationKeys,
      sel: ddIndex,
      parent: ddId,
    };
  } else if (data.type == "link") {
    annotDiv = "util_link_annot";
    ddId = "util_linkDD";
    annotData = {
      id: ddId,
      opt: annotationKeys,
      sel: ddIndex,
      parent: ddId,
    };
  }
  initExtDropdown(annotData);
  var annotListener = undefined;
  if (data.type == "node") {
    annotListener = nodeAnnotations;
  } else if (data.type == "link") {
    annotListener = linkAnnotations;
  }
  annotListener.update(data.annotations);
  annotListener["annotationKeys"] = annotationKeys;
  annotListener["selectedAnnotation"] = ddIndex;
  updateAnnoDD(data);
  annotListener.selectedAnnotationRegisterListener(function (val) {
    console.log("selectedAnnoation changed to " + val, data);
    updateAnnoDD(data);
  });
  document.getElementById(annotDiv).style.visibility = "visible";
}
function getSetNumberFunction(id) {
  return setSelectionNumber(id);
}
function setSelectionNumber(id) {
  return function (val) {
    if ((val == null) | (val == undefined)) {
      val = "None";
    } else {
      val = val.length;
    }
    document.getElementById(id).innerHTML = val;
  };
}
utilSocket.on("annotSel", function (data) {
  console.log("ANNOTATION SELECTION");
  if ((data.fn = !"sel")) return;
  tpye = data.type;
  val = data.val;
  if (data.val == null) {
    console.log("DANGER VAL IS NULL");
  }
  if (tpye == "node") {
    nodeAnnotations.selectedAnnotation = val;
  } else if (tpye == "link") {
    linkAnnotations.selectedAnnotation = val;
  }
});
utilSocket.on("selection", function (data) {
  // sessionData["selected"] = data;
});
// Turn update context depending on result
utilSocket.on("result", function (data) {
  // Receive annotation information from Server
  // if (data.project != sessionData["actPro"]) {
  //   return;
  // }
  if (data.data == "annotations") {
    if (data.project != pfile.name) {
      return;
    }
    console.log("NEW ANNOATIONS");
    console.log(data);
    updatedAnnotations(data);
  } else if (data.data == "selection") {
    updateSelection(data, pdata);
  }
});

utilSocket.on("reset", function (data) {
  if (data.type == "node") {
    pdata["cbnode"] = [];
    var content = document
      .getElementById("cbscrollbox")
      .shadowRoot.getElementById("box");
    removeAllChildNodes(content);
  } else if (data.type == "link") {
    pdata["selectedLinks"] = [];
  }
});
