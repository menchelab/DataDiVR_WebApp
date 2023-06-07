var highlightButton = [];
$(document).ready(function () {
  // initHighlightButton("util_isolate_bnt", "isolate", true);
  // initHighlightButton("util_bipartite_bnt", "bipartite", true);
  // initHighlightButton("util_store_highlight_btn", "store");
  // initHighlightButton("util_highlight_bnt", "highlight");
  // initCheckbox("util_use_highlight");
  // highlightButton.push("util_reset_highlight_btn");
  // $("#util_reset_highlight_btn").on("click", function () {
  //   statusID = "util_highlight_sm";
  //   resetSelection(
  //     "util_reset_highlight_btn",
  //     "project",
  //     statusID,
  //     "Reset Highlight"
  //   );
  // });
  // pdata.stateData.selectedRegisterListener(
  //   hideShow(["util_isolate_bnt", "util_bipartite_bnt"])
  // );
});
// Highlight on click
function initHighlightButton(id, mode, check = false) {
  highlightButton.push(id);
  if (check) {
    hideShow([id])(pdata.stateData.selected);
  }
  $("#" + id).on("click", function () {
    message = getSelections();
    message["mode"] = mode;
    message["id"] = id;
    message["text"] = document.getElementById(id).value;
    message["sm"] = "util_highlight_sm";
    if (document.getElementById("util_highlight_node_color").checked) {
      message["node_color"] = document
        .getElementById("util_highlight_node_color")
        .shadowRoot.querySelector("#color");
    }
    if (document.getElementById("util_use_link_highlight_color").checked) {
      message["link_color"] = document
        .getElementById("util_highlight_link_color")
        .shadowRoot.querySelector("#color");
    }
    // message["color"] = $("#util_highlight_color").colorbox.value;
    utilSocket.emit("highlight", message);
  });
}
// If No nodes are selected, disable isolate and bipartite buttons
function hideShow(ids) {
  return function (val) {
    var disable = false;
    if (val == null || val == undefined) {
      disable = true;
    } else if (val.length == 0) {
      disable = true;
    }
    for (var i = 0; i < ids.length; i++) {
      document.getElementById(ids[i]).disabled = disable;
      document.getElementById(ids[i]).style.display = disable
        ? "none"
        : "block";
    }
  };
}
