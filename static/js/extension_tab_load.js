function addTab(tabList, defaultImg) {
  // tabList is the id of the <ul> element that contains the tabs.
  // defaultImg is the path to the default image to be used if no image is provided.
  // This function will add a new tab to the tabList. If there is a free tab, it will be used. Otherwise, a new tab will be created.
  var listOfTabs = document.getElementById(tabList);
  var fragment_number = listOfTabs.childNodes.length + 1;
  var listObject = document.createElement("li");
  var link = null;
  var tab_baseName = listOfTabs.children[0].children[0].href.split("#")[1];
  var img = document.createElement("img");
  var childList = listOfTabs.children;

  // Get the next free tab.
  for (var i = 0; i < childList.length; i++) {
    tab = childList[i];
    tab_href = tab.children[0].href.split("#")[1];
    // If there is no reference to this tab and the innerHTML is empty, it is free. Take it.
    if (!document.getElementById(tab_href) && tab.innerHTML == "") {
      tab.style.display = "inline";
      link = tab.children[0];
      link.href = "#" + tab_href;
      img = link.children[0];
      tabId = tab_href;
      break;
    }
  }

  // If no free tab is found, create a new one.
  if (!link) {
    link = document.createElement("a");
    link.href = "#" + tab_baseName + fragment_number;
    tabId = tab_baseName + fragment_number;
    link.appendChild(img);
    listObject.appendChild(link);
    listOfTabs.appendChild(listObject);
  }

  // Set the image of the tab.
  var tab_img = document.getElementById("tab_img");
  if (tab_img) {
    img.src = tab_img.src;
    document.getElementById("tab_img").remove();
  } else {
    img.src = defaultImg;
  }

  img.draggable = "false";
  img.onmousedown = "return false";
  img.height = "40";
  img.width = "40";

  var new_tab = document.getElementById("tab_to_add");
  if (new_tab != null) {
    new_tab.display = "inline";
    new_tab.id = tabId;
  }
}
