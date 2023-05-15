


$(document).ready(function () {
  //LOAD NAMESPACE MENU TAB 1
    //LOAD NAMESPACE MENU TAB 1
   
    //GetDbFileNames1();
    //console.log("this");
    $("#new_namespace_name").hide();
    $(function () {
      $("#namespaces").selectmenu(
        {
          classes:{
              "ui-selectmenu-open": "twozerozero-open",
          },
      });

    });

    $(function () {
      $("#tabsUL").tabs();
    });

    $('#namespaces').on('selectmenuselect', function () {
        var name = $('#namespaces').find(':selected').text();
        console.log(name);
        //UpdateNamespace(name);

    });




    $("#upload_buttonJSON").button();
    $("#new_namespace_nameJSON").show();
    // $("input:radio[name='namespace']").change( function() {
    //     if ($(this).val() == "New") {
    //         $("#new_namespace_nameJSON").show();
    //     } else {
    //         $("#new_namespace_nameJSON").show();
    //     }
    // });
    
    $('#upload_form').on('change input', function() {
        console.log("changed!");
        var formData = new FormData(document.getElementById('upload_form'));
        for (var pair of formData.entries()) {
        console.log(pair[0]+ ', ' + pair[1]); 
        } 
      });
      
      
      
      $("#upload_formJSON").submit(function(event) {
        event.preventDefault();
      
        var form = $(this);
        var formData = new FormData(this);
        if (formData.get("namespaceJSON") == 'existing') {
          formData.append('existing_namespace', $('#namespaces').val());
        }
        let it = formData.keys();

        let result = it.next();
        while (!result.done) {
       console.log(result); // 1 3 5 7 9
          console.log(formData.get(result.value))
       result = it.next();
      }
        dbprefix = "http://"+ window.location.href.split("/")[2]; // Not sure why no todo it like this. Maybe if the server runs on a different ip than the uploader?
        var url = dbprefix + "/uploadfilesJSON";
        console.log(url);
        console.log(formData);
        $.ajax({
          type: "POST",
          url: url,
          data: formData, // serializes the form's elements.
          cache: false,
          contentType: false,
          processData: false,
          success: function(data)
          {
			console.log(data); 
			 $("#upload_message").html(data);
			  
          },
        error: function (err) {
            console.log("Upload failed!"); 
		    $("#upload_message").html("Upload failed");
			
        }
        });
      
      });
      


    



});

