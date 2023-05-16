
var socket;
function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

var uid = makeid(10);

$(document).ready(function(){
    ///set up and connect to socket
    console.log('http://' + document.domain + ':' + location.port + '/doku');
    socket = io.connect('http://' + document.domain + ':' + location.port + '/doku');
    socket.io.opts.transports = ['websocket'];
    
    socket.on('connect', function() {
        var msg = {usr:uid}
        socket.emit('join', msg);    
    });
    socket.on('status', function(data) {
    });
    socket.on('ex', function(data) {
        console.log("server returned: " + JSON.stringify(data));
        switch(data.fn)
        {
            case 'mkB':
                makeButton(data.id, data.msg, data.msg);
                break;


            case 'cht':
                $('#'+data.id).tabs('option', 'active',data.msg);
                break;

            case 'scb':
                if (data.usr != uid){
                    settextscroll(data.id, data.msg);
                }
                
                break;
                
            case 'rem_butt_del':
                if ($('#' + data.parent).find('#' + data.id).length) {
                    // found! -> remove in only in that div
                    $('#' + data.parent).find('#' + data.id).remove();
                }
                break;

            
            case 'rem_butt_del_sbox':
                var box = document.getElementById(data.parent).shadowRoot.getElementById("box");
                 $(box).find('#' + data.id).remove();
                break;

            case 'tgl':
                $('#'+ data.id).val(data.val)
                break;



            case 'sel':
                // SPECIAL CASE: Refresh Page When loading new project
                if (data.id == "projects"){
                    var url = window.location.href.split('?')[0] + "?usr="  + username + "&project=" + data.opt;
                    console.log(url);
                    window.location.href = url;

                }

                $('#'+ data.id).val(data.opt);
                $('#'+ data.id).selectmenu("refresh");

                break; 

            case 'sli':
                if (data.usr != uid){
                    $('#'+ data.id).slider('value', data.val);

                }
                break; 
            case 'tex':
                    var text = document.getElementById(data.id).shadowRoot.getElementById("text");
                    text.value= data.val;
                break;
            case 'chk':
                    $('#'+ data.id).prop('checked', (data.val));
                    
                break;
            case 'col':
                    var color = document.getElementById(data.id).shadowRoot.getElementById("color");
                    color.value =data.val ;
                break;
            case 'but':
                    console.log(data.id + " clicked");

                break;
            
            case 'sres':
                console.log(data.val.length);

                document.getElementById("sres").shadowRoot.getElementById("box").innerHTML = ''
                for (let i = 0; i < data.val.length; i++) {
                    var p = document.createElement("mc-sresult");
                    p.setAttribute("id", data.val[i].id);
                    //console.log(data.val[i].id);
                    p.setAttribute("name", data.val[i].name);
                    p.setAttribute("style", "width=150px");
                    p.setAttribute("color" , '#' + Math.floor(Math.random()*16777215).toString(16));
                    document.getElementById("sres").shadowRoot.getElementById("box").appendChild(p);
                }
                break;
                

            case 'sres_butt_clicked':
                    console.log(data.id);
                    //ue4("selectnode", data)
                    break;

            case 'plotly2js':
                //console.log(data["parent"]);
                if(document.getElementById(data["parent"])){
                    const config = {displayModeBar: false}; // this is the line that should hide the navbar.
                    const layout = {};
                    var gdata = JSON.parse(data["val"])
                    //console.log(gdata);
               
                    Plotly.newPlot(data["parent"], gdata, layout, config);
                    var myPlot = document.getElementById(data["parent"]);
                    myPlot.on('plotly_click', function(data){
                        if (data.points[0].hasOwnProperty("meta")){  // add callback to nodebuttton automatically if provided
                            console.log(data.points[0].meta);
                            socket.emit('ex', { msg: "none", id: "none",val: data.points[0].meta,  fn: 'node'});
                        }
                        else if (data.points[0].hasOwnProperty("label")){
                            console.log(data.points[0].label);
                        }
                        else if(data.points[0].hasOwnProperty("text")){
                            console.log(data.points[0].text);
                        }else {
                            console.log(data.points[0]);
                        }
                    });
                        
                    // this is the line that hides the bar for real
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) {
                    NavBar[i].style.visibility = "hidden";
                    }
                }
                break;
        

        }
        
        
    });

});



function settextscroll(id, val) {
    var box = document.getElementById(id).shadowRoot.getElementById("box");
    $(box).scrollTop(val[0]);
    $(box).scrollLeft(val[1]);
}
