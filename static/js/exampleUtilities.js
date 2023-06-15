function initExtDropdown(data) {
  console.log("init dropdown", data.id);
  var element = document.getElementById(data.id);
  if (element) {
    var select = element.shadowRoot.getElementById("sel");
    var count = element.shadowRoot.querySelector("#count");
    var content = element.shadowRoot.getElementById("content");
    var socketDomain = element.getAttribute("socketDomain");
    if (!socketDomain) socketDomain = "main";

    if (data.hasOwnProperty("opt")) {
      removeAllChildNodes(content);
      cmul = 70;
      //.log(data.opt.length)
      console.log(data.opt);
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

function setUpdateMessage(element = undefined, id = undefined, text = "Test") {
  if (!element) var element = document.getElementById(id);
  element.innerHTML = text;
  element.style.opacity = 1;
  setTimeout(function () {
    element.style.opacity = 0;
  }, 3000);
}
