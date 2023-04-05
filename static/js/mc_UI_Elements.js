// SOME FUNCTIONS TO CREATE MULTICASTED (via socketIO) UI ELEEMENTS LIKE BUTTONS, DROPDOWNS, SLIDERS, CHECKBOXES

function initDropdown(id, data, active) {

  $('#' + id).selectmenu();
  $('#' + id).find('option').remove().end();
  //$('#' + id).selectmenu( "destroy" );
  $('#' + id).selectmenu();
  for (let i = 0; i < data.length; i++) {
  $('#' + id).append(new Option(data[i]));
  }

  $('#' + id).val(active);
  $('#' + id).selectmenu("refresh");

  $('#' + id).off('selectmenuselect');
  $('#' + id).on('selectmenuselect', function() {
    var name = $('#' + id).find(':selected').text();
    socket.emit('ex', { id: id, opt: name, fn: "sel" });
    ///logger($('#selectMode').val());
  });

}


/// a test to add json string as attribute to dropdown option
function initDropdownX(id, data, active) {

  $('#' + id).selectmenu();

  for (let i = 0; i < data.length; i++) {

    var addata ={id:i, size: 99, city: makeid(5)};
    
    $('<option>').val("object.val").text(data[i]).attr('data-x', JSON.stringify(addata)).appendTo('#' + id);
  }

  $('#' + id).val(active);
  $('#' + id).selectmenu("refresh");

  $('#' + id).on('selectmenuselect', function() {
    var name = $('#' + id).find(':selected').text();
    var x = $('#' + id).find(':selected').attr("data-x");
    socket.emit('ex', { id: id, opt: name, fn: "sel", data: x, usr: uid });
    console.log(JSON.parse(x));
  });

}


function initSlider(id) {

  $('#' + id).slider({
    animate: true,
    range: "max",
    min: 0,
    max: 255,
    value: 128,
    slide: function(event, ui) {
      socket.emit('ex', { id: id, val: ui.value, fn: "sli", usr: uid});
    }
  });

}


function initCheckbox(id) {
  $('#' + id).on("click", function() {
    socket.emit('ex', { id: id, val: $('#' + id).is(":checked"), fn: "chk" ,usr: uid});
  });

}


function initButton(id) {
  $('#' + id).on("click", function() {
    var $this = $(this);
    socket.emit('ex', { id: id, val: "clicked", fn: "but", usr: uid});
  });
}








function makeid(length) {
  var result = '';
  var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  var charactersLength = characters.length;
  for (var i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() *
      charactersLength));
  }
  return result;
}
function deactivateTabs(id) {
  // Deactivate all tabs which are not contained in the html
  var tabs = document.getElementById(id);
  var items = tabs.getElementsByTagName('li');
  for (var i = 0; i < items.length; i++) {
    hyperlink = items[i].getElementsByTagName('a')[0];
    var id = hyperlink.href.split('#')[1];
    if (!(document.getElementById(id))) {
      items[i].style.display = 'none';
    } else {
      items[i].style.display = 'inline';
    }
  };
};
function setHref(id, uniprot,link) {
  var href = link.replace("<toChange>", uniprot)
  console.log(href)
  $('#' + id).attr('href', href);
}
function followLink(link) {
  var url = "http://" + window.location.href.split("/")[2];
  window.location.href= url + link;
}