utilSocket = io.connect("http://" + location.host + "/Util");
// receive status
utilSocket.on("status", function (data) {
  if (highlightButton.includes(data.id)) {
    for (var i = 0; i < highlightButton.length; i++) {
      document.getElementById(highlightButton[i]).disabled = false;
    }
  }
  button = document.getElementById(data.id);
  button.value = data.text;
  button.disabled = false;
  sm = data.sm;
  if (sm != undefined) {
    setStatus(data.status, sm, data.message);
  }
  if (["util_store_highlight_btn"].includes(data.id)) {
    updateProjectList(data.projectName);
  }
  $("#" + data.id).removeClass("loadingButton");
});
// Turn of the Highlight button on other clients
utilSocket.on("started", function (data) {
  if (highlightButton.includes(data.id)) {
    for (var i = 0; i < highlightButton.length; i++) {
      document.getElementById(highlightButton[i]).disabled = true;
    }
  }
  button = document.getElementById(data.id);
  button.value = "";
  button.disabled = true;
  $("#" + data.id).addClass("loadingButton");
});
// receive status
utilSocket.on("ex", function (data) {
  console.log("server returned: " + JSON.stringify(data));
  switch (data.fn) {
    case "dropdown":
      initExtDropdown(data);
  }
});
