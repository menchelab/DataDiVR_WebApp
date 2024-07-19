
var socket;
var newcon = true;
var logAll = true;
var isPreview = false; logjs
var isMain = false;
var isUE4 = false;


if (String(navigator.userAgent).includes("UnrealEngine")) {
    isUE4 = true;

} else {
    console.log("not ue4")
}

function logjs(data, id) {
    if (document.getElementById("userid")) {
        var content = document.getElementById(id).shadowRoot.getElementById("box");
        let x = content.innerHTML;
        if (x.length > 2000) {
            removeAllChildNodes(content);
        }

        $(content).prepend('<pre><code>' + JSON.stringify(data, undefined, 2) + '</pre></code>');

    }
}

var uid = makeid(10);
console.log("Logged in as " + uid);

ue.interface.projectLoaded = function(data) {
    console.log(data);
    var text = '{"id":"x", "success": "true", "fn": "projectLoaded"}';
    var out = JSON.parse(text);
    out["usr"] = uid;
    socket.emit('ex', out);
    logjs(data, 'scrollbox_debug_1');
};

ue.interface.nodelabels = function(data) {
    console.log(data);
    var text = '{"id":"nl", "data": [], "fn": "x"}';
    var out = JSON.parse(text);
    out.data = data;
    socket.emit('ex', out);
};

ue.interface.nodelabelclicked = function(data) {
    console.log(data);
    var text = '{"id":"node", "val": -1, "fn": "node"}';
    var out = JSON.parse(text);
    out.val = data;
    socket.emit('ex', out);
};

ue.interface.speech = function(data) {
    console.log(data);
    var text = '{"id":"node", "val": -1, "fn": "textinput"}';
    var out = JSON.parse(text);
    x = JSON.parse(data)
    out.id = x.id;
    out.val = x.text;
    socket.emit('ex', out);

};



function updateMcElements() {
    dynelem = document.getElementsByClassName("GD");

    for (let i = 0; i < dynelem.length; i++) {
        switch (dynelem[i].getAttribute('type')) {
            case 'textinput':
                socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), parent: dynelem[i].getAttribute('container'), fn: "submit_butt", val: "init" });
                break;
            case 'slider':
                socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "sli", val: "init" });
                break;
            case 'dropdown':
                socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "dropdown", val: "init" });
                break;
            case "module":
                dynelem[i].init();
                break;
            case "annotationDD":
                socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "annotationDD", val: "init" });
                break;

            // this seems not to change anything 
            // case "ue4":
            //     socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "ue4", val: "init" });
            //     break;
            // case "button":
            //     socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "resetlayout", val: "init" });
            //     break;
        }
        //console.log(dynelem[i].getAttribute('container'));
    }
    // add here init values for new joined client
    socket.emit('ex', { usr: uid, id: "cbaddNode", fn: "addNode", val: "init" });
    socket.emit('ex', { usr: uid, id: "analyticsPathNode1", fn: "analytics", val: "init" });
    socket.emit('ex', { usr: uid, id: "analyticsPathNode2", fn: "analytics", val: "init" });
    socket.emit('ex', { usr: uid, id: "annotationOperation", fn: "annotation", val: "init" });
    socket.emit('ex', { usr: uid, id: "annotationRun", fn: "annotation", val: "init" });
    socket.emit('ex', { usr: uid, id: "layoutInit", fn: "layout", val: "init" });
    //socket.emit('ex', { usr:uid, id: "annotationInit", fn: "annotation", val:"init"})
    socket.emit('ex', {usr:uid,  val: "init", id: "annotation-dd-1", fn: "annotation"});
    socket.emit('ex', {usr:uid,  val: "init", id: "annotation-dd-2", fn: "annotation"});
    socket.emit('ex', {usr:uid,  val: "init", id: "init", fn: "enrichment"});
    // socket.emit("ex", {usr:uid,  fn: "legend_scene_display", id: "legend_scene_display", val: "init"});

    // VRrooms
    socket.emit('ex', {usr:uid,  val: "init", id: "VRrooms", fn: "dropdown"});



}

function speakNow(text) {
    if ('speechSynthesis' in window) {
        // Speech Synthesis supported 🎉
        const message = new SpeechSynthesisUtterance(text);
        message.lang = "en-US";

        const voices = speechSynthesis.getVoices().filter(voice => voice.lang === "en-US");
        console.log(voices)
        message.voice = voices[1];

        speechSynthesis.speak(message);
    } else {
        // Speech Synthesis Not Supported 😣
        console.log("Sorry, your browser doesn't support text to speech!");
    }

}

$(document).ready(function() {

    // speakNow("Hello Human! Welcome to the data diver.")

    if (document.getElementById("preview")) {
        isPreview = true;
    }
    if (document.getElementById("main")) {
        isMain = true;
    }

    if (document.getElementById("scrollbox1")) {
        document.getElementById("scrollbox1").style.display = "none";
    }
    if (document.getElementById("scrollbox2")) {
        document.getElementById("scrollbox2").style.display = "none";
    }

    if (document.getElementById("userid")) {
        document.getElementById("userid").innerHTML = uid;
    }


    ///set up and connect to socket
    console.log('http://' + document.domain + ':' + location.port + '/main');
    socket = io.connect('http://' + document.domain + ':' + location.port + '/main');
    socket.io.opts.transports = ['websocket'];

    socket.on('connect', function() {
        var msg = { usr: uid }
        socket.emit('join', msg);
    });


    socket.on('disconnect', function() {
        console.log("disconnected - trying to connect")
        socket.emit('join', {});
        if (document.getElementById("disconnected")) {
            document.getElementById("disconnected").style.display = "block"
        }
        if (document.getElementById("outer")) {
            document.getElementById("outer").style.backgroundColor = "rgb(239 0 0 / 34%)"
        }
        location.reload()

    });

    socket.on('status', function(data) {
        //console.log(data)
        if (data.usr == uid) {
            if (isMain || isPreview) {
                // START initialization routine
                socket.emit('ex', { id: "projDD", fn: "dropdown", val: "init", usr: uid });
            }

            if (document.getElementById("disconnected")) {
                document.getElementById("disconnected").style.display = "none"
            }
            if (document.getElementById("outer")) {
                document.getElementById("outer").style.backgroundColor = "rgb(0 0 0 / 0%)"
            }
            socket.emit('ex', { usr:uid, id: "analytics", fn: "dropdown", val:"init"});

            // VRrooms
            socket.emit('ex', { usr:uid, id: "VRrooms", fn: "dropdown", val:"init"});


        }
        //CONNECTION Established - initialize the project (Ui elements initialize when project changes)

    });


    socket.on('ex', function(data) {
        logjs(data, 'scrollbox_debug_0');

        //if (logAll && data.usr == uid)
        //{
        console.log("server returned: " + JSON.stringify(data));

        //}

        switch (data.fn) {
            case 'projectLoaded':

                updateMcElements();

                if (data.usr == uid) {

                    if (isPreview) {
                        // Wait until ui is initialized
                        setTimeout(function() {
                            initialized = true;
                            makeNetwork();
                        }, 2000);
                    }

                }

                break;

            case 'mkB':
                makeButton(data.id, data.msg, data.msg);
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

            case 'col':
                // SPECIAL CASE: Refresh Page When loading new project
                var colorpicker = document.getElementById(data.id).shadowRoot.getElementById("color");
                colorpicker.value = data.val;

                //  $('#'+ data.id).value(data.val);
                console.log(data.val);

                break;

            case 'sli':
                //$('#'+ data.id).slider('value', data.val);
                if (document.getElementById(data.id)) {
                    var slider = document.getElementById(data.id).shadowRoot.getElementById("myRange");
                    slider.value = data.val;
                }
                ue4(data["fn"], data);
                break;
            /* 
            case 'tex':
                    var text = document.getElementById(data.id).shadowRoot.getElementById("text");
                    text.value= data.val;
                break;*/
            case 'scb':
                //settextscroll(data.id, data.msg);
                break;

            case 'makeNodeButton':
                //console.log(data.val.length);
                document.getElementById(data.parent).style.display = "block";
                var content = document.getElementById(data.parent).shadowRoot.getElementById("box");
                removeAllChildNodes(content);
                for (let i = 0; i < data.val.length; i++) {
                    $(content).append("<mc-button id = 'button" + i + " 'val= '" + data.val[i].id + "' name = '" + data.val[i].name + "' w = '118' fn = 'node' color = '" + rgbToHex(data.val[i].color[0] * 0.5, data.val[i].color[1] * 0.5, data.val[i].color[2] * 0.5) + "' ></mc-button>");
                }
                if (data.id == "search") {
                    document.getElementById("searchcount").innerHTML = "[" + data["val"].length + "]";
                }
                if (data.id == "children") {
                    document.getElementById("linkL2").innerHTML = data["nid"] + "<br><h6>" + "[" + data["val"].length + " Links]</h6>";

                }
                break;

            case "cbaddNode":
                var content = document.getElementById('cbscrollbox').shadowRoot.getElementById("box");
                removeAllChildNodes(content);
                for (let i = 0; i < data.val.length; i++) {
                    $(content).append("<mc-button id = 'button" + i + " 'val= '" + data.val[i].id + "' name = '" + data.val[i].name + "' w = '118' fn = 'node' color = '" + rgbToHex(data.val[i].color[0] * 0.5, data.val[i].color[1] * 0.5, data.val[i].color[2] * 0.5) + "' ></mc-button>");
                }
                break;
            case "colorbox":
                document.getElementById(data.id).shadowRoot.getElementById("color").style.backgroundColor = 'rgba(' + data.r + ',' + data.g + ',' + data.b + ',' + data.a * 255 + ')';
                break;

            case "updateTempTex":
                if (isPreview) {
                    // predefine layoutpaths here to send them afterwards to webgl if both are set within one socket connection
                    let layoutNodesHiPath, layoutNodesLowPath;
                    for (let i = 0; i < data.textures.length; i++) {
                        let textureData = data.textures[i];
                        if (textureData.channel === "layoutNodesHi") { layoutNodesHiPath = textureData.path; continue; }
                        if (textureData.channel === "layoutNodesLow") { layoutNodesLowPath = textureData.path; continue; }
                        downloadTempTexture(textureData.path, textureData.channel);
                    }
                    if (layoutNodesHiPath !== undefined && layoutNodesLowPath !== undefined) { updateLayoutTemp(layoutNodesLowPath, layoutNodesHiPath); }

                } else {
                    ue4(data["fn"], data);
                }
                break;



            case 'node':
                if (document.getElementById("nodeL2")) {
                    document.getElementById("nodeL2").innerHTML = data["val"]["n"] + "<br><h6>" + "[" + data["nch"] + " Links]</h6>";
                    document.getElementById("nodeRawdata").textContent = JSON.stringify(data["val"], undefined, 2);
                    document.getElementById("nodecount").innerHTML = "[" + data["val"]["id"] + "]";
                }
                if (isPreview) { setUserLabelPos(data["val"]["id"], data["val"]["n"]); }
                //$("#piechart").append("<d3pie-widget data = '{a: " + Math.floor(Math.random()*100) + ", b: " + Math.floor(Math.random()*100) + ", c:" + Math.floor(Math.random()*100) + ", d:" + Math.floor(Math.random()*100) + ", e:" + Math.floor(Math.random()*100) + ", f:" + Math.floor(Math.random()*100) + ", g:" + Math.floor(Math.random()*100) + "}' color = '#" + Math.floor(Math.random()*16777215).toString(16) + "'></d3draw-widget>");
                ue4(data["fn"], data);
                if (document.getElementById("mProtein_container")) {


                    if (data.val.hasOwnProperty("protein_info")) {
                        var styldata = []
                        initDropdown("protnamedown", data.val.uniprot, data.val.uniprot[0]);
                        if (data.val.protein_info.length > 0) {
                            for (let i = 0; i < Object.keys(data.val.protein_info[0]).length; i++) {
                                if (Object.keys(data.val.protein_info[0])[i] != 'file') {
                                    styldata.push(Object.keys(data.val.protein_info[0])[i])
                                }

                            }
                            document.getElementById("mProtein_container").style.display = "block";
                            initDropdown("protstyle", styldata, styldata[0]);
                        }

                    }
                    else {
                        document.getElementById("mProtein_container").style.display = "none";

                    }
                }

                break;

            case 'loadProtein':
                ue4(data["fn"], data);
                break;

            case 'svg':
                var container = document.getElementById(data["parent"])
                container.innerHTML = data["val"];
                //document.getElementById("patch_3").addEventListener("click", function() {
                //  alert('www.link1.com')
                //});
                break;

            case 'plotly':
                console.log("plotly");

                $("#plotlytest").load("/Plotly/TEST111");
                var mvar = [];
                $(".slicetext").each(function() {
                    console.log("found");
                    mvar.push($(this))
                    $(this).click(function() {
                        0
                        alert("Handler for .click() called.");
                    });
                });
                console.log(mvar);

                break;

            case 'plotly2js':
                //console.log(data["parent"]);
                if (document.getElementById(data["parent"])) {
                    const config = { displayModeBar: false }; // this is the line that should hide the navbar.
                    const layout = {};
                    var gdata = JSON.parse(data["val"])
                    //console.log(gdata);

                    Plotly.newPlot(data["parent"], gdata, layout, config);
                    var myPlot = document.getElementById(data["parent"]);
                    myPlot.on('plotly_click', function(data) {
                        if (data.points[0].hasOwnProperty("meta")) {  // add callback to nodebuttton automatically if provided
                            console.log(data.points[0].meta);
                            socket.emit('ex', { msg: "none", id: "none", val: data.points[0].meta, fn: 'node' });
                        }
                        else if (data.points[0].hasOwnProperty("label")) {
                            console.log(data.points[0].label);
                        }
                        else if (data.points[0].hasOwnProperty("text")) {
                            console.log(data.points[0].text);
                        } else {
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



            case 'dropdown':
                if (document.getElementById(data.id)) {
                    var select = document.getElementById(data.id).shadowRoot.getElementById("sel");
                    var count = document.getElementById(data.id).shadowRoot.querySelector("#count");
                    var hasCount = document.getElementById(data.id).hasCount;
                    var content = document.getElementById(data.id).shadowRoot.getElementById("content");


                    if (data.hasOwnProperty('opt')) {

                        removeAllChildNodes(content);
                        // cmul = 70;
                        //.log(data.opt.length)
                        let optionColors = genOptionColorGradient(data.opt.length);
                        for (let i = 0; i < data.opt.length; i++) {
                            // $(content).append("<mc-button id = 'button"+ i + " 'val= '"+ i + "' name = '"+ data.opt[i] +  "' w = '375' parent = '"+ data.parent + "' fn = 'dropdown' color = '" + rgbToHex(Math.floor(Math.random()*cmul),Math.floor(Math.random()*cmul),Math.floor(Math.random()*cmul)) + "' ></mc-button>");
                            $(content).append("<mc-button id = 'button" + i + " 'val= '" + i + "' name = '" + data.opt[i] + "' w = '375' parent = '" + data.parent + "' fn = 'dropdown' color = '" + optionColors[i] + "' ></mc-button>");
                        }
                        select.value = data.opt[data.sel]
                        if (hasCount === true) { count.innerHTML = " [" + data.opt.length + "]"; }
                        content.style.display = "none";
                    } else {
                        //this comes from the buttons
                        select.value = data.name;
                        content.style.display = "none";
                    }

                    if (isPreview) {
                        if (data.id == "layoutsDD") {
                            actLayout = data.sel;
                            makeNetwork();
                        }
                        if (data.id == "layoutsRGBDD") {
                            actLayoutRGB = data.sel;
                            makeNetwork();
                        }
                        if (data.id == "linksRGBDD") {
                            actLinksRGB = data.sel;
                            makeNetwork();
                        } 
                        if(data.id == "linksDD"){                            
                            actLinks = data.sel;
                            makeNetwork();
                        }                       



                    }
                    if (data.id == "analytics") {
                        $('.analyticsOption').css('display', 'none');
                        switch (data.name) {
                            case "Degree Distribution":
                                $("#analyticsSelectedDegree").css('display', 'inline-block');
                                break;
                            case "Closeness":
                                $("#analyticsSelectedCloseness").css('display', 'inline-block');
                                break;
                            case "Shortest Path":
                                $("#analyticsSelectedPath").css('display', 'inline-block');
                                break;
                            case "Eigenvector":
                                $("#analyticsSelectedEigenvector").css('display', 'inline-block');
                                break;
                            case "Mod-based Communities":
                                $("#analyticsSelectedModcommunity").css('display', 'inline-block');
                                break;
                            case "Clustering Coefficient":
                                $("#analyticsSelectedClusteringCoeff").css('display', 'inline-block');
                                break;
                            case "Clustering Coefficient":
                                $("#analyticsSelectedClusteringCoeff").css('display', 'inline-block');
                                break;
                            // add bindings for options display here

                        }
                    }
                    // VRrooms
                    if (data.id == "VRrooms"){
                        switch (data.name){
                            case "Dome":
                                ue4(data["name"], data.name);
                                break;
                            case "Landscape":
                                ue4(data["name"], data.name);
                                break;
                            // case "Platforms":
                            //     ue4(data["name"], data.name);
                            //     break;
                        }
                    }

                    //if (data.id == "layout"){
                    if (data.id == "layoutModule") {
                        $('.layoutOption').css('display', 'none');
                        switch (data.name) {
                            case "Random":
                                $("#layoutSelectRandom").css('display', 'inline-block');
                                break;
                            case "Eigenlayout":
                                $("#layoutSelectEigen").css('display', 'inline-block');
                                break;
                            case "cartoGRAPHs Local":
                                $("#layoutSelectCartoLocal").css('display', 'inline-block');
                                break;
                            case "cartoGRAPHs Global":
                                $("#layoutSelectCartoGlobal").css('display', 'inline-block');
                                break;
                            case "cartoGRAPHs Importance":
                                $("#layoutSelectCartoImportance").css('display', 'inline-block');
                                break;
                            case "Spectral":
                                $("#layoutSelectSpectral").css('display', 'inline-block');
                                break;
                            // add bindings for options display here4
                        }
                    }

                    if (data.id == "layoutsDD") {
                        switch (data.id) {
                            case "layoutsDD": // if change in DD for layout = change layout title 

                                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "layouts", "graphlayout");

                                layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                                layouts_DD.setAttribute("sel", parseInt(data.sel));
                                layouts_DD.setAttribute("value", pfile.layouts[data.sel]);

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);

                                //console.log("C_DEBUG updating Buttons in layoutsDD: ", nextButton.getAttribute("val"));

                                break;
                        }
                    }


                    if (data.id == "layoutsRGBDD") {
                        switch (data.id) {
                            case "layoutsRGBDD": // if change in DD for node colors = change node colors in network and legend

                                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "layoutsRGB", "graphlayout_nodecolors");
                                Legend_displayNodeInfobyID(pfile.name, data.sel);

                                layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                                layoutsRGB_DD.setAttribute("sel", parseInt(data.sel));
                                layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[data.sel]);

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);
                                //console.log("C_DEBUG updating Buttons in layoutsRGBDD: ", nextButton.getAttribute("val"));

                                break;
                        }
                    }

                    if (data.id == "linksRGBDD") {
                        switch (data.id) {
                            case "linksRGBDD": // if change in DD for link colors = change link colors in network and legend

                                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "linksRGB", "graphlayout_linkcolors");
                                Legend_displayLinkInfobyID(pfile.name, data.sel);

                                if (pfile.linksRGB.length <= data.sel) {
                                    linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                                    linksRGB_DD.setAttribute("sel", parseInt(0));
                                    linksRGB_DD.setAttribute("value", pfile.linksRGB[0]);
                                } else {
                                    linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                                    linksRGB_DD.setAttribute("sel", parseInt(data.sel));
                                    linksRGB_DD.setAttribute("value", pfile.linksRGB[data.sel]);
                                }

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);
                                //console.log("C_DEBUG updating Buttons in linksRGBDD: ", nextButton.getAttribute("val"));

                                break;
                        }
                    }
                
                    if(data.id == "linksDD") {
                        switch (data.id){
                            case "linksDD": // if change in DD for link colors = change link colors in network and legend
                                
                                if (pfile.links.length <= data.sel) {
                                    links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                                    links_DD.setAttribute("sel", parseInt(0));
                                    links_DD.setAttribute("value", pfile.links[0]);
                                } else {
                                    links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                                    links_DD.setAttribute("sel", parseInt(data.sel));
                                    links_DD.setAttribute("value", pfile.links[data.sel]);
                                }

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);

                                break;
                        }
                    }
                
                ue4(data["fn"], data);
                }
                break;
                

            case "project":

                //clearProject();
                //if (data["usr"]==uid){
                pfile = data["val"];
                //console.log("C_DEBUG: in CASE PROJECT _ project data = ", pfile);

                // init analytics container
                document.getElementById('analyticsContainer').innerHTML = '';
                document.getElementById('nodecounter').innerHTML = pfile['nodecount'] + ' NODES';
                document.getElementById('linkcounter').innerHTML = pfile['linkcount'] + ' LINKS';

                var content = document.getElementById('cbscrollbox').shadowRoot.getElementById("box");
                removeAllChildNodes(content);

                // initial info on L E G E N D P A N E L based on DD
                Legend_displayGraphInfo(pfile.name);
                Legend_displayfirstFile(pfile.name);

                if (data.sel == NaN || data.sel == undefined) {
                    data.sel = 0;
                }
                
                //console.log("C_DEBUG: project data sel = ", data.sel);

                Legend_displayNodeInfobyID(pfile.name, data.sel);
                Legend_displayLinkInfobyID(pfile.name, data.sel);
                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "layouts", "graphlayout");
                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "layouts", "graphlayout_nodecolors");
                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "layouts", "graphlayout_linkcolors");


                // set arrow buttons with index of DD
                nextButton = document.getElementById("forwardstep");
                nextButton.setAttribute('val', data.sel);
                backButton = document.getElementById("backwardstep");
                backButton.setAttribute('val', data.sel);

                //console.log("C_DEBUG updating Buttons while load project: ", nextButton.getAttribute("val"));

                if (isPreview) {
                    downloadProjectTextures(); // download textures for preview, report when done
                }
                ue4(data["fn"], data);

                //}    
                break;

            case "cnl":
                ue4(data["fn"], data);
                break;

            case "checkbox":
                if (document.getElementById(data["id"])) {
                    document.getElementById(data["id"]).shadowRoot.getElementById("box").checked = data["val"];
                }
                if (data["id"] == "linkblendCHK") {
                    ue4("linkblend", data);
                }

                // checkbox for analytics LINKS
                if(data["id"]=="cbdefinelinklist"){
                    socket.emit("ex", {
                            fn: "checkbox",
                            id: "cbdefinedlinkslist",
                            val: data["val"]
                        });
                break;
                }

            case "ue4":

                if (data.id == "resetlayout") {

                    // set value to 0
                    var reset_value = 0;
                    data.val = reset_value;

                    // socket.emit("ex", {
                    //     fn: "legend_scene_display",
                    //     id: "legend_scene_display",
                    //     val: reset_value
                    // });

                    // update legend 
                    Legend_displayNodeInfobyID(pfile.name, reset_value);
                    Legend_displayLinkInfobyID(pfile.name, reset_value);
                    Legend_displayGraphLayoutbyID(pfile.name, reset_value, "layouts", "graphlayout");
                    Legend_displayGraphLayoutbyID(pfile.name, reset_value, "layouts", "graphlayout_nodecolors");
                    Legend_displayGraphLayoutbyID(pfile.name, reset_value, "layouts", "graphlayout_linkcolors");

                    // update DD 
                    layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");   
                    layouts_DD.setAttribute("sel", parseInt(reset_value));
                    layouts_DD.setAttribute("value", pfile.layouts[reset_value]);

                    layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                    layoutsRGB_DD.setAttribute("sel", parseInt(reset_value));
                    layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[reset_value]);

                    linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                    linksRGB_DD.setAttribute("sel", parseInt(reset_value));             
                    linksRGB_DD.setAttribute("value", pfile.linksRGB[reset_value]);

                    links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                    links_DD.setAttribute("sel", parseInt(forwardidx));
                    links_DD.setAttribute("value", pfile.links[forwardidx]);

                    // update arrow buttons with new index
                    nextButton = document.getElementById("forwardstep");    
                    nextButton.setAttribute('val', reset_value);        
                    backButton = document.getElementById("backwardstep");           
                    backButton.setAttribute('val', reset_value);                

                    if (isPreview) {
                        actLayout = reset_value;
                        actLayoutRGB = reset_value;
                        actLinks = reset_value
                        actLinksRGB = reset_value;
                        makeNetwork();
                    }
                }   


                if (data.id == "forwardstep") {

                    // 1. get index of DD layout and set backwardidx
                    var layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    var forwardidx = parseInt(layouts_DD.getAttribute("sel"));
                    console.log("C_DEBUG in ue4 forwardidx from layoutsDD = ", forwardidx);

                    // 2. then add an index to it
                    forwardidx = NEWIndexforwardstep(pfile.layouts.length);
                    console.log("C_DEBUG in ue4 forwardstep = ", forwardidx);

                    // // is that necessary??
                    // socket.emit("ex", {
                    //     fn: "legend_scene_display",
                    //     id: "legend_scene_display",
                    //     val: forwardidx
                    // });

                    // 3. then update dropdowns accordingly
                    // link colors 
                    let actLinksRGB;
                    if (pfile.linksRGB.length < forwardidx) {
                        linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                        linksRGB_DD.setAttribute("sel", parseInt(0));
                        linksRGB_DD.setAttribute("value", pfile.linksRGB[0]);
                        actLinksRGB = 0;

                    } else {
                        linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                        linksRGB_DD.setAttribute("sel", parseInt(forwardidx));
                        linksRGB_DD.setAttribute("value", pfile.linksRGB[forwardidx]);
                        actLinksRGB = forwardidx;
                    }

                    // layouts
                    layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    layouts_DD.setAttribute("sel", parseInt(forwardidx));
                    layouts_DD.setAttribute("value", pfile.layouts[forwardidx]);
                    //console.log("C_DEBUG changed Layouts: ", forwardidx);

                    // layoutRGB
                    layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                    layoutsRGB_DD.setAttribute("sel", parseInt(forwardidx));
                    layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[forwardidx]);
                    //console.log("C_DEBUG changed Layouts Colors: ", forwardidx);

                    // links
                    let actLinks;
                    if (pfile.links.length < forwardidx) {
                        links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                        links_DD.setAttribute("sel", parseInt(0));
                        links_DD.setAttribute("value", pfile.links[0]);

                        actLinks = 0;
                        console.log("C_DEBUG in Links < than forwardidx");

                    } else {
                        links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                        links_DD.setAttribute("sel", parseInt(forwardidx));
                        links_DD.setAttribute("value", pfile.links[forwardidx]);

                        actLinks = forwardidx;
                        console.log("C_DEBUG in Links forwardidx: ", forwardidx);

                    }
                    console.log("C_DEBUG changed Links: ", forwardidx);
                    
                    Legend_displayNodeInfobyID(pfile.name, forwardidx);
                    Legend_displayLinkInfobyID(pfile.name, forwardidx);
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout");
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout_nodecolors");
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout_linkcolors");

                    data["val"] = forwardidx;
                    //console.log("C_DEBUG: data val forwardidx = ", data["val"]);

                    if (isPreview) {
                        actLayout = forwardidx;
                        actLayoutRGB = forwardidx;
                        makeNetwork();
                    }


                }


                if (data.id == "backwardstep") {

                    // 1. get index of DD layout and set backwardidx
                    var layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    var backwardidx = parseInt(layouts_DD.getAttribute("sel"));
                    //console.log("C_DEBUG in ue4 backwardidx from layoutsDD = ", backwardidx);

                    // 2. then add an index to it
                    backwardidx = NEWIndexbackwardstep(pfile.layouts.length);
                    //console.log("C_DEBUG in ue4 backwardidx = ", backwardidx);

                    // socket.emit("ex", {
                    //     fn: "legend_scene_display",
                    //     id: "legend_scene_display",
                    //     val: backwardidx
                    // });

                    // 3. then update dropdowns accordingly
                    // link colors
                    let actLinksRGB;
                    if (pfile.linksRGB.length <= backwardidx) {
                        linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                        linksRGB_DD.setAttribute("sel", parseInt(0));
                        linksRGB_DD.setAttribute("value", pfile.linksRGB[0]);
                        actLinksRGB = 0;

                    } else {
                        linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                        linksRGB_DD.setAttribute("sel", parseInt(backwardidx));
                        linksRGB_DD.setAttribute("value", pfile.linksRGB[backwardidx]);
                        actLinksRGB = backwardidx;
                    }
                    //console.log("C_DEBUG changed Link colors: ", backwardidx);

                    // layouts
                    layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    layouts_DD.setAttribute("sel", parseInt(backwardidx));
                    layouts_DD.setAttribute("value", pfile.layouts[backwardidx]);
                    //console.log("C_DEBUG changed Layouts: ", backwardidx);

                    // layoutRGB
                    layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                    layoutsRGB_DD.setAttribute("sel", parseInt(backwardidx));
                    layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[backwardidx]);
                    //console.log("C_DEBUG changed Layouts Colors: ", backwardidx);


                    // links
                    let actLinks;
                    if (pfile.links.length <= backwardidx) {
                        links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                        links_DD.setAttribute("sel", parseInt(0));
                        links_DD.setAttribute("value", pfile.links[0]);
                        actLinks = 0;

                    } else {
                        links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                        links_DD.setAttribute("sel", parseInt(backwardidx));
                        links_DD.setAttribute("value", pfile.links[backwardidx]);
                        actLinks = backwardidx;
                    }
                    //console.log("C_DEBUG changed Links: ", backwardidx);

                    Legend_displayNodeInfobyID(pfile.name, backwardidx);
                    Legend_displayLinkInfobyID(pfile.name, backwardidx);
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout");
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout_nodecolors");
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout_linkcolors");

                    data["val"] = backwardidx;
                    //console.log("C_DEBUG: data val back = ", data["val"]);

                    if (isPreview) {
                        actLayout = backwardidx;
                        actLayoutRGB = backwardidx;
                        makeNetwork();
                    }

                }
                
                ue4("but", data);
                //console.log("C_DEBUG: ue4 data = ", data);

                break;

            case "textinput":
                console.log(data.val + " --- " + data.id);
                if (document.getElementById(data.id)) {
                    var content = document.getElementById(data.id).shadowRoot.getElementById("text");
                    content.value = data.val;
                }

                break;

            case "chatmessage":
                displayChatText(data);
                // console.log("C_DEBUG: print text message")
                // ue4(data["fn"], data); // NOT TESTED IF Username taken from ue4
                break;
            

            case "analytics":

                if (data.id == "analyticsDegreePlot") {
                    const config = { displayModeBar: false };
                    const layout = {};
                    let plot_data = JSON.parse(data["val"]);

                    Plotly.newPlot(data["target"], plot_data, layout, config);

                    let plotIFrame = document.getElementById(data["target"]);

                    let user = data.usr;
                    let targetDiv = data.target;
                    plotIFrame.on('plotly_click', function(data) {
                        if (data.event.button !== 0) { return; }

                        let clickedBarX = Math.floor(data.points[0].x);

                        console.log(clickedBarX);

                        let request = {
                            fn: "analytics",
                            id: "analyticsDegreeRun",
                            highlight: clickedBarX,
                            target: targetDiv,
                            usr: user
                        }

                        socket.emit("ex", request);
                    });

                    plotIFrame.style.display = "inline-block";
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) { NavBar[i].style.visibility = "hidden"; }
                }

                if (data.id == "analyticsClosenessPlot") {
                    const config = { displayModeBar: false };
                    const layout = {};
                    let plot_data = JSON.parse(data["val"]);

                    Plotly.newPlot(data["target"], plot_data, layout, config);

                    let plotIFrame = document.getElementById(data["target"]);

                    let user = data.usr;
                    let targetDiv = data.target;
                    plotIFrame.on('plotly_click', function(data) {
                        if (data.event.button !== 0) { return; }

                        let clickedBarX = data.points[0].x;

                        console.log(clickedBarX);

                        let request = {
                            fn: "analytics",
                            id: "analyticsClosenessRun",
                            highlight: clickedBarX,
                            target: targetDiv,
                            usr: user
                        }

                        socket.emit("ex", request);
                    });

                    plotIFrame.style.display = "inline-block";
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) { NavBar[i].style.visibility = "hidden"; }
                }

                if (data.id == "analyticsEigenvectorPlot") {
                    const config = { displayModeBar: false };
                    const layout = {};
                    let plot_data = JSON.parse(data["val"]);

                    Plotly.newPlot(data["target"], plot_data, layout, config);

                    let plotIFrame = document.getElementById(data["target"]);

                    let user = data.usr;
                    let targetDiv = data.target;
                    plotIFrame.on('plotly_click', function(data) {
                        if (data.event.button !== 0) { return; }

                        let clickedBarX = data.points[0].x;

                        console.log(clickedBarX);

                        let request = {
                            fn: "analytics",
                            id: "analyticsEigenvectorRun",
                            highlight: clickedBarX,
                            target: targetDiv,
                            usr: user
                        }

                        socket.emit("ex", request);
                    });

                    plotIFrame.style.display = "inline-block";
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) { NavBar[i].style.visibility = "hidden"; }
                }

                if (data.id == "analyticsClusteringCoeffPlot") {
                    const config = { displayModeBar: false };
                    const layout = {};
                    let plot_data = JSON.parse(data["val"]);

                    Plotly.newPlot(data["target"], plot_data, layout, config);

                    let plotIFrame = document.getElementById(data["target"]);

                    let user = data.usr;
                    let targetDiv = data.target;
                    plotIFrame.on('plotly_click', function(data) {
                        if (data.event.button !== 0) { return; }

                        let clickedBarX = data.points[0].x;

                        console.log(clickedBarX);

                        let request = {
                            fn: "analytics",
                            id: "analyticsClusteringCoeffRun",
                            highlight: clickedBarX,
                            target: targetDiv,
                            usr: user
                        }

                        socket.emit("ex", request);
                    });

                    plotIFrame.style.display = "inline-block";
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) { NavBar[i].style.visibility = "hidden"; }
                }
                if (data.id == "analyticsPathNode1") {
                    let button = document.getElementById("analyticsPathNode1").shadowRoot.getElementById("name");
                    if (data.val != "init") {
                        button.innerHTML = data.val.name;
                        button.style.color = data.val.color;
                    }
                }
                if (data.id == "analyticsPathNode2") {
                    let button = document.getElementById("analyticsPathNode2").shadowRoot.getElementById("name");
                    if (data.val != "init") {
                        button.innerHTML = data.val.name;
                        button.style.color = data.val.color;
                    }
                }

                if (data.id == "analyticsPathInfo") {
                    let container = document.getElementById('analyticsContainer');
                    // clear before refill
                    document.getElementById('analyticsContainer').innerHTML = "";

                    let numPathsAll = data.val.numPathsAll;
                    let numPathCurrent = data.val.numPathCurrent;
                    let pathLen = data.val.pathLength;

                    // fill analytics container with usefull information
                    // current path number
                    let currentPathDiv = document.createElement('div');
                    currentPathDiv.style.margin = "3px";
                    currentPathDiv.innerHTML = `Current Path : : <span style="font-size:18px; font-weight:bold">${numPathCurrent}</span>`;
                    container.appendChild(currentPathDiv);

                    // number of all paths
                    let numPathsDiv = document.createElement('div');
                    numPathsDiv.style.margin = "3px"
                    numPathsDiv.innerHTML = `Number of Paths : : <span style="font-size:18px; font-weight:bold">${numPathsAll}</span>`;
                    container.appendChild(numPathsDiv);

                    // path length
                    let pathLenDiv = document.createElement('div');
                    pathLenDiv.style.margin = "3px"
                    pathLenDiv.innerHTML = `Path Length : : <span style="font-size:18px; font-weight:bold">${pathLen}</span>`;
                    container.appendChild(pathLenDiv);

                }


                if (data.id == "clearAnalyticsContainer") {
                    // prevent if you havent switched !!!!
                    document.getElementById('analyticsContainer').innerHTML = "";
                }

                break;

            case "annotationDD":

                if (data.id == "initDD") {
                    const annotationDD1 = document.getElementById("annotation-dd-1");
                    const annotationDD2 = document.getElementById("annotation-dd-2");
                    annotationDD1.updateOptions(data.options);
                    annotationDD2.updateOptions(data.options);

                    // here init function to retreive type and annotation

                    return;
                }

                // defined annoID here as executor of the methods which it triggered; task separation by val here!
                let annoID = document.getElementById(data.id);

                if (data.val == "demo") {
                    annoID.demo();
                }

                if (data.val == "initDD") {
                    annoID.setType(data.valType);
                    annoID.setAnnotation(data.valAnnotation);
                }

                if (data.val == "close") {
                    annoID.close();
                }

                if (data.val == "openType") {
                    annoID.generateSelectionType(data.valOptions);
                }

                if (data.val == "openSub") {
                    annoID.setType(data.valSelected);
                    annoID.generateSelectionSub(data.valOptions);
                }

                if (data.val == "openMain") {
                    annoID.setSub(data.valSelected);
                    annoID.generateSelectionMain(data.valOptions);
                }

                if (data.val == "annotationSelected") {
                    annoID.setAnnotation(data.valSelected);
                }

                if (data.val == "setTypeDisplay") { annoID.setType(data.valType); }

                break;



            case "annotation":

                const annotationDD1 = document.getElementById("annotation-dd-1");
                const annotationDD2 = document.getElementById("annotation-dd-2");

                if (data.id == "annotationOperation") {
                    let value = data.val;
                    if (value == "init") { return; }
                    let button = document.getElementById("annotationOperation").shadowRoot.getElementById("name");
                    let annotationLegend2 = document.getElementById("annotationColorA2");
                    let annotationLegendR = document.getElementById("annotationColorR");
                    if (value == true) {
                        button.innerHTML = "SINGLE";
                        annotationDD2.style.display = "inline-block";
                        document.getElementById("annotation-Operations").style.display = "inline-block";
                        annotationLegendR.style.display = "block";
                        annotationLegend2.style.display = "block";
                    }
                    if (value == false) {
                        button.innerHTML = "OPERATION";
                        annotationDD2.style.display = "none";
                        document.getElementById("annotation-Operations").style.display = "none";
                        annotationLegendR.style.display = "none";
                        annotationLegend2.style.display = "none";
                    }
                }

                break;

            case "legendfileswitch":

                if (data.id == "legend_forward") {
                    Legend_switchingFiles_forward(pfile.name);

                } else if (data.id == "legend_backward") {
                    Legend_switchingFiles_backward(pfile.name);

                }
                break


            case "layout":
                if (data.id == "layoutInit") {
                    if (data.val == "init") { return; }

                    // display log
                    let logContainer = document.getElementById("layoutLog");
                    let logBtnShow = document.getElementById("layoutLogShow");
                    let logBtnHide = document.getElementById("layoutLogHide")
                    if (data.val === true) {
                        logContainer.style.display = "block";
                        logBtnHide.style.display = "block";
                        logBtnShow.style.display = "none";
                    }
                    else {
                        logContainer.style.display = "none";
                        logBtnHide.style.display = "none";
                        logBtnShow.style.display = "block";
                    }

                    // display buttons
                    handleLayoutExistsDisplay(data.val.selectedLayoutGenerated);
                }

                if (data.id == "showLog") {
                    let logContainer = document.getElementById("layoutLog");
                    let logBtnShow = document.getElementById("layoutLogShow");
                    let logBtnHide = document.getElementById("layoutLogHide")
                    if (data.val === true) {
                        logContainer.style.display = "block";
                        logBtnHide.style.display = "block";
                        logBtnShow.style.display = "none";
                    }
                    else {
                        logContainer.style.display = "none";
                        logBtnHide.style.display = "none";
                        logBtnShow.style.display = "block";
                    }
                }

                if (data.id == "addLog") {
                    let layoutLog = log2HTML(data.log);
                    let layoutLogContainer = $("#layoutLog");
                    layoutLogContainer.append(layoutLog);

                }

                if (data.id == "layoutExists") {
                    handleLayoutExistsDisplay(data.val);
                }

                break;

            case "gotonode":
                ue4(data["fn"], data);
                //alert("rrrrrreeee");
                break;

            case "moduleState":
                if (data.val == true) {
                    document.getElementById(data.id).maximizeModule();
                }
                if (data.val == false) {
                    document.getElementById(data.id).minimizeModule();
                }
                break;

            case "enrichment":
                if (data.id == "init") {
                    $("#enrichment-colors").css('display', 'none');
                    $("#enrichment-note-result").css('display', 'none');
                    $("#enrichment-note-features").css('display', 'none');
                    if (data.valHideNote == false) { $("#enrichment-note-features").css('display', 'block'); }

                    let button_container = document.getElementById("enrichment-query").shadowRoot.getElementById("box");
                    removeAllChildNodes(button_container);
                    for (let i = 0; i < data.valQuery.length; i++) {
                        $(button_container).append("<mc-button id = 'button" + i + " 'val= '" + data.valQuery[i].id + "' name = '" + data.valQuery[i].name + "' w = '118' fn = 'node' color = '" + rgbToHex(data.valQuery[i].color[0] * 0.5, data.valQuery[i].color[1] * 0.5, data.valQuery[i].color[2] * 0.5) + "' ></mc-button>");
                    }
                    break;
                }

                if (data.id == "enrichment-import") {
                    let button_container = document.getElementById("enrichment-query").shadowRoot.getElementById("box");
                    removeAllChildNodes(button_container);
                    for (let i = 0; i < data.val.length; i++) {
                        $(button_container).append("<mc-button id = 'button" + i + " 'val= '" + data.val[i].id + "' name = '" + data.val[i].name + "' w = '118' fn = 'node' color = '" + rgbToHex(data.val[i].color[0] * 0.5, data.val[i].color[1] * 0.5, data.val[i].color[2] * 0.5) + "' ></mc-button>");
                    }
                    break;
                }

                if (data.id == "enrichment-clear") {
                    let button_container = document.getElementById("enrichment-query").shadowRoot.getElementById("box");
                    removeAllChildNodes(button_container);
                }

                if (data.id == "enrichment-run") {
                    const config = { displayModeBar: false };
                    const layout = {};
                    let plot_data = JSON.parse(data["valPlot"]);
                    let payload = data.valPayload
                    let targetName = "enrichment-container";
                    let targetContainer = document.getElementById(targetName);
                    let user = data.usr;

                    Plotly.newPlot(targetName, plot_data, layout, config);
                    targetContainer.on('plotly_click', function(data) {
                        if (data.event.button !== 0) { return; }

                        let clickedBar = data.points[0].customdata[0];
                        let clickedFeature = data.points[0].customdata[1];

                        let request = {
                            fn: "enrichment",
                            id: "enrichment-run",
                            val: [clickedBar, clickedFeature, payload[0], payload[1], payload[2]], // bar id, feature. feature type, test result dict, query ids list
                            usr: user
                        }

                        socket.emit("ex", request);
                    });

                    targetContainer.style.display = "inline-block";
                    const NavBar = document.getElementsByClassName("modebar-container");
                    for (let i = 0; i < NavBar.length; i++) { NavBar[i].style.visibility = "hidden"; }
                }

                if (data.id == "enrichment-colors") {
                    if (data.val == true) { $("#enrichment-colors").css('display', 'block'); }
                }
                if (data.id == "enrichment-note-result") {
                    $("#enrichment-note-result").css('display', 'block');
                    $("#enrichment-note-result").html(data.val)
                }

            // case "legend_scene_display":
            //     if (data.has_scenes === true) {
            //         $("#legend-scene-description-container").css('display', 'block');
            //         $("#legend-scene-description-element").html("SCENE : : " + data.text)
            //     }
            //     else {
            //         $("#legend-scene-description-container").css('display', 'none');
            //         $("#legend-scene-description-element").html("")
            //     }
        }
    });

});


//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------