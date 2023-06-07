function initButton(id) {
  $("#" + id).on("click", function () {
    var $this = $(this);
    socket.emit("ex", { id: id, val: $this.val(), fn: "but" });
  });
  if (id == "backwardstep") {
    initBackwardStep();
  } else if (id == "forwardstep") {
    initForwardStep();
  } else if (id == "reset") {
    initResetButton();
  }
}
function nextLayout(id) {
  var idx = $("#" + id).prop("selectedIndex");
  var numOptions = $("#" + id).children().length;
  if (idx == numOptions - 1) {
    idx = 0;
  } else {
    idx++;
  }
  $("#" + id).prop("selectedIndex", idx);
  $("#" + id).selectmenu("refresh");
}
function prevLayout(id) {
  var idx = $("#" + id).prop("selectedIndex");
  if (idx == 0) {
    idx = -1;
  } else {
    idx--;
  }
  $("#" + id).prop("selectedIndex", idx);
  $("#" + id).selectmenu("refresh");
}
function initBackwardStep() {
  $("#backwardstep").on("click", function () {
    if (document.getElementById("chbXYZ").checked == true) {
      prevLayout("layouts");
    }
    if (document.getElementById("chbNrgb").checked == true) {
      prevLayout("nodecolors");
    }
    if (document.getElementById("chbLXYZ").checked == true) {
      prevLayout("links");
    }
    if (document.getElementById("chbLrgb").checked == true) {
      prevLayout("linkcolors");
    }
  });
}
function initForwardStep() {
  $("#forwardstep").on("click", function () {
    if (document.getElementById("chbXYZ").checked == true) {
      nextLayout("layouts");
    }
    if (document.getElementById("chbNrgb").checked == true) {
      nextLayout("nodecolors");
    }
    if (document.getElementById("chbLXYZ").checked == true) {
      nextLayout("links");
    }
    if (document.getElementById("chbLrgb").checked == true) {
      nextLayout("linkcolors");
    }
  });
}
