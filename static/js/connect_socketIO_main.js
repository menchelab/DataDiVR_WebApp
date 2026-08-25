



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
console.log("C_DEBUG in connect_sockeIO_main : Logged in as " + uid);

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

ue.interface.paintnodesADD = function(data) {
    console.log(data);
    var text = '{"id":"paintnodes", "data": [], "fn": "paintnodes", "op":"ADD"}';
    var out = JSON.parse(text);
    out["usr"] = uid;
    out.data = data;
    socket.emit('ex', out);
};

ue.interface.paintnodesSUB = function(data) {
    console.log(data);
    var text = '{"id":"paintnodes", "data": [], "fn": "paintnodes", "op":"SUB"}';
    var out = JSON.parse(text);
    out["usr"] = uid;
    out.data = data;
    socket.emit('ex', out);
};

ue.interface.manLabel = function(data) {
    //console.log(data);
    var text = '{"id":"manLabel", "x": 0, "y":0, "z":0, "fn": "manLabel"}';
    var out = JSON.parse(text);
    var input = JSON.parse(data);
    out["usr"] = uid;
    out["name"] = input.text;
    out.x = input.x;
    out.y = input.y;
    out.z = input.z;
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
            case "ue4":
                socket.emit('ex', { usr: uid, id: dynelem[i].getAttribute('id'), fn: "ue4", val: "init" });
                break;
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

    // buttons morphing
    // console.log("Forwardstep value before emit:", forwardstep);
    // socket.emit('ex', { usr: uid, id: "forwardstep", fn: "ue4", val: "init" });
    // console.log("Backwardstep value before emit:", backwardstep);
    // socket.emit('ex', { usr: uid, id: "backwardstep", fn: "ue4", val: "init" });
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
        console.log("disconnected - SocketIO will auto-reconnect")
        // socket.emit('join', {}) is a no-op here since the socket is disconnected
        if (document.getElementById("disconnected")) {
            document.getElementById("disconnected").style.display = "block"
        }
        if (document.getElementById("outer")) {
            document.getElementById("outer").style.backgroundColor = "rgb(239 0 0 / 34%)"
        }
        // location.reload() was removed: it triggered a full page reload on every disconnect,
        // causing a new connection → projDD init → project event broadcast to room →
        // VR reloads its project. SocketIO's built-in reconnect handles this correctly.
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

        switch (data.fn) {
            case 'projectLoaded':

                // updateMcElements() is safe to call unconditionally here — server-side
                // all init responses now go only to the requesting socket (flask.request.sid),
                // so there is no cross-client race.  Restricting it to uid==usr broke
                // /main and /preview initialization because VR triggers projectLoaded
                // with its own uid, so browsers never ran updateMcElements at all.
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

            // suggested label candidates for the current selection (VR paint/lasso +
            // GUI clipboard, combined - see label_events.get_active_node_selection).
            // Rendered into whichever of the paint / clipboard panels are present.
            case "labelSuggestions":
                ["labelSuggestBox", "labelSuggestBoxCb"].forEach(function (boxId) {
                    var box = document.getElementById(boxId);
                    if (!box) return; // panel not present on this page
                    var content = box.shadowRoot.getElementById("box");
                    removeAllChildNodes(content);
                    if (data.val.length === 0) {
                        var reasonText = {
                            "selection_too_small": "No suggestions: select at least 2 nodes first.",
                            "no_annotation_data": "No suggestions: this project has no annotation/attribute data to compare against.",
                            "no_terms_found": "No suggestions: no attribute terms found among the selected nodes."
                        }[data.reason] || "No suggestions.";
                        $(content).append("<div style='padding:4px;'>" + reasonText + "</div>");
                    } else {
                        for (let i = 0; i < data.val.length; i++) {
                            var candidate = data.val[i];
                            var flag = candidate.significant ? "" : " · below p&lt;0.05";
                            $(content).append(
                                "<div style='padding:4px;'>" + candidate.term +
                                " <span style='opacity:0.6;'>(" + candidate.type + ", p=" + candidate.pvalue.toExponential(2) + flag + ")</span></div>"
                            );
                        }
                    }
                });
                break;
            case "colorbox":
                document.getElementById(data.id).shadowRoot.getElementById("color").style.backgroundColor = 'rgba(' + data.r + ',' + data.g + ',' + data.b + ',' + data.a * 255 + ')';
                break;


            


            case "updateTempTex":
                console.log("C_DEBUG: updateTempTex event received with data:", data);



                // if (isPreview) {
                //     // predefine layoutpaths here to send them afterwards to webgl if both are set within one socket connection
                //     let layoutNodesHiPath, layoutNodesLowPath;
                //     for (let i = 0; i < data.textures.length; i++) {
                //         let textureData = data.textures[i];
                //         if (textureData.channel === "layoutNodesHi") { layoutNodesHiPath = textureData.path; continue; }
                //         if (textureData.channel === "layoutNodesLow") { layoutNodesLowPath = textureData.path; continue; }
                //         downloadTempTexture(textureData.path, textureData.channel);
                //     }
                //     if (layoutNodesHiPath !== undefined && layoutNodesLowPath !== undefined) { updateLayoutTemp(layoutNodesLowPath, layoutNodesHiPath); }

                // } else {
                ue4(data["fn"], data);
                //}
                break;






            case 'node':
                if (document.getElementById("nodeL2")) {
                    document.getElementById("nodeL2").innerHTML = data["val"]["n"] + "<br><h6>" + "[" + data["nch"] + " Links]</h6>";
                    document.getElementById("nodeRawdata").innerHTML = renderNodeInfoHTML(data["val"]);
                    document.getElementById("nodecount").innerHTML = "[" + data["val"]["id"] + "]";
                }
                if (isPreview) { setUserLabelPos(data["val"]["id"], data["val"]["n"]); }
                //$("#piechart").append("<d3pie-widget data = '{a: " + Math.floor(Math.random()*100) + ", b: " + Math.floor(Math.random()*100) + ", c:" + Math.floor(Math.random()*100) + ", d:" + Math.floor(Math.random()*100) + ", e:" + Math.floor(Math.random()*100) + ", f:" + Math.floor(Math.random()*100) + ", g:" + Math.floor(Math.random()*100) + "}' color = '#" + Math.floor(Math.random()*16777215).toString(16) + "'></d3draw-widget>");
                ue4(data["fn"], data);


                // FROM TILL ?
                // if (document.getElementById("mProtein_container")) {
                //     if (data.val.hasOwnProperty("protein_info")) {
                //         var styldata = []
                //         initDropdown("protnamedown", data.val.uniprot, data.val.uniprot[0]);
                //         if (data.val.protein_info.length > 0) {
                //             for (let i = 0; i < Object.keys(data.val.protein_info[0]).length; i++) {
                //                 if (Object.keys(data.val.protein_info[0])[i] != 'file') {
                //                     styldata.push(Object.keys(data.val.protein_info[0])[i])
                //                 }
                //             }
                //             document.getElementById("mProtein_container").style.display = "block";
                //             initDropdown("protstyle", styldata, styldata[0]);
                //         }
                //     }
                //     else {
                //         document.getElementById("mProtein_container").style.display = "none";
                //     }
                // }


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
                
            
                console.log("C_DEBUG:in plotly2js case :", data["parent"]);


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
                            case "Force-Directed":
                                $("#layoutSelectFD").css('display', 'inline-block');
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
                            case "Spring":
                                $("#layoutSelectSpring").css('display', 'inline-block');
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
                        }
                    }

                    if (data.id == "linksRGBDD") {
                        switch (data.id) {
                            case "linksRGBDD": // if change in DD for link colors = change link colors in network and legend

                                Legend_displayGraphLayoutbyID(pfile.name, data.sel, "linksRGB", "graphlayout_linkcolors");
                                Legend_displayLinkInfobyID(pfile.name, data.sel);

                                // if (pfile.linksRGB.length < data.sel || pfile.linksRGB.length == 0) {
                                //     linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                                //     linksRGB_DD.setAttribute("sel", parseInt(0));
                                //     linksRGB_DD.setAttribute("value", pfile.linksRGB[0]);
                                // } else {
                                //     linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                                //     linksRGB_DD.setAttribute("sel", parseInt(data.sel));
                                //     linksRGB_DD.setAttribute("value", pfile.linksRGB[data.sel]);
                                // }

                                linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                                linksRGB_DD.setAttribute("sel", parseInt(data.sel));
                                linksRGB_DD.setAttribute("value", pfile.linksRGB[data.sel]);

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);
                        }
                    }
                
                    if(data.id == "linksDD") { // THIS CASE DOES NOT EXIST -> one link list per project 
                        switch (data.id){
                            case "linksDD": // if change in DD for link colors = change link colors in network and legend
                                
                                //if (pfile.links.length <= data.sel) {
                                links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                                links_DD.setAttribute("sel", parseInt(0));
                                links_DD.setAttribute("value", pfile.links[0]);
                                // } else {
                                //     links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                                //     links_DD.setAttribute("sel", parseInt(data.sel));
                                //     links_DD.setAttribute("value", pfile.links[data.sel]);
                                // }

                                // update arrow buttons with new index
                                nextButton = document.getElementById("forwardstep");
                                nextButton.setAttribute('val', data.sel);
                                backButton = document.getElementById("backwardstep");
                                backButton.setAttribute('val', data.sel);
                        }
                    }
                
                    // When projDD updates (on initial connect or project change from /main),
                    // also init the layout/color/link dropdowns.  projDD has class PD not GD
                    // so updateMcElements() skips it; this is the only reliable hook that
                    // fires both on first load AND on project switch for web-UI clients.
                    // The project event that sets pfile always arrives before dropdown/projDD,
                    // so GD.pfile is already loaded server-side when these reach the server.
                    if (data.id == "projDD" && (isMain || isPreview)) {
                        socket.emit('ex', { usr: uid, id: "layoutsDD",    fn: "dropdown", val: "init" });
                        socket.emit('ex', { usr: uid, id: "layoutsRGBDD", fn: "dropdown", val: "init" });
                        socket.emit('ex', { usr: uid, id: "linksDD",      fn: "dropdown", val: "init" });
                        socket.emit('ex', { usr: uid, id: "linksRGBDD",   fn: "dropdown", val: "init" });
                    }

                ue4(data["fn"], data);
                //console.log("C_DEBUG: sending data to UE4 : ", data);
                }
                break;
                

            case "project":
                //HAMLO
                //clearProject();
                //if (data["usr"]==uid){
                pfile = data["val"];
                //console.log("C_DEBUG: in CASE PROJECT _ project data = ", pfile);

                // init analytics container
                document.getElementById('analyticsContainer').innerHTML = '';
                $("#analyticsModCommunityGroups").empty();
                document.getElementById('nodecounter').innerHTML = pfile['nodecount'] + ' NODES';
                document.getElementById('linkcounter').innerHTML = pfile['linkcount'] + ' LINKS';

                var content = document.getElementById('cbscrollbox').shadowRoot.getElementById("box");
                removeAllChildNodes(content);

                // clear node search / node info / connections / selections / label
                // suggestions - all keyed to nodes of the project we just left
                clearProjectDependentPanels();

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

                break;
                

            case "manLabel":
                if (data.id == "manLabel") {
                    ue4(data["fn"], data);
                }

                // if (data.id == "resetlayout") {

                //     data.val = 0;
                //     // socket.emit("ex", {
                //     //     fn: "legend_scene_display",
                //     //     id: "legend_scene_display",
                //     //     val: reset_value
                //     // });
                    
                //     // update legend 
                //     Legend_displayNodeInfobyID(pfile.name, 0);
                //     Legend_displayLinkInfobyID(pfile.name, 0);
                //     Legend_displayGraphLayoutbyID(pfile.name, 0, "layouts", "graphlayout");
                //     Legend_displayGraphLayoutbyID(pfile.name, 0, "layouts", "graphlayout_nodecolors");
                //     Legend_displayGraphLayoutbyID(pfile.name, 0, "layouts", "graphlayout_linkcolors");

                //     // update DD 
                //     // layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");   
                //     // layouts_DD.setAttribute("sel", parseInt(0));
                //     // layouts_DD.setAttribute("value", pfile.layouts[0]);

                //     // layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                //     // layoutsRGB_DD.setAttribute("sel", parseInt(0));
                //     // layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[0]);

                //     // linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                //     // linksRGB_DD.setAttribute("sel", parseInt(0));             
                //     // linksRGB_DD.setAttribute("value", pfile.linksRGB[0]);

                //     //links_DD = document.getElementById("linksDD").shadowRoot.getElementById("sel");
                //     //links_DD.setAttribute("sel", parseInt(0));
                //     //links_DD.setAttribute("value", pfile.links[0]);

                //     // update arrow buttons with new index
                //     nextButton = document.getElementById("forwardstep");    
                //     nextButton.setAttribute('val', 0);        
                //     backButton = document.getElementById("backwardstep");           
                //     backButton.setAttribute('val', 0);                

                //     // trigger dropdown cases
                //     // this is quick fix since no reset button in VR exe implemented (button id = resetlayout")
                    
                //     data.fn = "dropdown";
                //     data.id = "layoutsDD";
                //     socket.emit("ex", data);
                //     data.id = "layoutsRGBDD";
                //     socket.emit("ex", data);
                //     data.id = "linksRGBDD";
                //     socket.emit("ex", data);

                //     if (isPreview) {
                //         actLayout = 0;
                //         actLayoutRGB = 0;
                //         actLinksRGB = 0;
                //         makeNetwork();
                //     }
                // }   
            case "ue4":
                if (data.id == "forwardstep") {

                    var forwardidx = parseInt(data.val);

                    // 1. get index of DD layout and set idx
                    var layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    forwardidx = parseInt(layouts_DD.getAttribute("sel"));
                    console.log("C_DEBUG: forwardidx = ", forwardidx);

                    // 2. then add an index to it
                    forwardidx = NEWIndexforwardstep(pfile.layouts.length);
                    console.log("C_DEBUG: NEW forwardidx = ", forwardidx);

                    //let actLinksRGB;
                    //if (pfile.linksRGB.length == 0 || pfile.linksRGB.length <= forwardidx) {
                    linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                    linksRGB_DD.setAttribute("sel", parseInt(forwardidx));
                    linksRGB_DD.setAttribute("value", pfile.linksRGB[forwardidx]);

                    // layouts
                    layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    layouts_DD.setAttribute("sel", parseInt(forwardidx));
                    layouts_DD.setAttribute("value", pfile.layouts[forwardidx]);

                    // layoutRGB
                    layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                    layoutsRGB_DD.setAttribute("sel", parseInt(forwardidx));
                    layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[forwardidx]);

                    Legend_displayNodeInfobyID(pfile.name, forwardidx);
                    Legend_displayLinkInfobyID(pfile.name, forwardidx);
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout");
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout_nodecolors");
                    Legend_displayGraphLayoutbyID(pfile.name, forwardidx, "layouts", "graphlayout_linkcolors");
                    
                    if (isPreview) {
                        actLayout = forwardidx;
                        actLayoutRGB = forwardidx;
                        actLinksRGB = forwardidx;
                        makeNetwork();
                    }

                    data["val"] = forwardidx;
                    console.log("C_DEBUG: forward - data[val] = ", data["val"]);
                }


                if (data.id == "backwardstep") {
                    
                    var backwardidx = parseInt(data.val);

                    // 1. get index of DD layout and set backwardidx
                    var layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    backwardidx = parseInt(layouts_DD.getAttribute("sel"));

                    // 2. then add an index to it
                    backwardidx = NEWIndexbackwardstep(pfile.layouts.length);

                    //let actLinksRGB;
                    //if (pfile.linksRGB.length == 0 || pfile.links.length <= backwardidx) {
                    linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                    linksRGB_DD.setAttribute("sel", parseInt(backwardidx));
                    linksRGB_DD.setAttribute("value", pfile.linksRGB[backwardidx]);
                    //actLinksRGB = parseInt(0);     
                    // } else {
                    //     linksRGB_DD = document.getElementById("linksRGBDD").shadowRoot.getElementById("sel");
                    //     linksRGB_DD.setAttribute("sel", parseInt(backwardidx));
                    //     linksRGB_DD.setAttribute("value", pfile.linksRGB[backwardidx]);
                    //     actLinksRGB = backwardidx;
                    // }

                    // layouts
                    layouts_DD = document.getElementById("layoutsDD").shadowRoot.getElementById("sel");
                    layouts_DD.setAttribute("sel", parseInt(backwardidx));
                    layouts_DD.setAttribute("value", pfile.layouts[backwardidx]);

                    // layoutRGB
                    layoutsRGB_DD = document.getElementById("layoutsRGBDD").shadowRoot.getElementById("sel");
                    layoutsRGB_DD.setAttribute("sel", parseInt(backwardidx));
                    layoutsRGB_DD.setAttribute("value", pfile.layoutsRGB[backwardidx]);

                    Legend_displayNodeInfobyID(pfile.name, backwardidx);
                    Legend_displayLinkInfobyID(pfile.name, backwardidx);
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout");
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout_nodecolors");
                    Legend_displayGraphLayoutbyID(pfile.name, backwardidx, "layouts", "graphlayout_linkcolors");

                    if (isPreview) {
                        actLayout = backwardidx;
                        actLayoutRGB = backwardidx;
                        actLinksRGB = backwardidx;
                        makeNetwork();
                    }

                    data["val"] = backwardidx;
                    console.log("C_DEBUG: backward - data[val] = ", data["val"]);

                }
                ue4("but", data);
                break;


                
            case "textinput":
                console.log(data.val + " --- " + data.id);
                if (document.getElementById(data.id)) {
                    var content = document.getElementById(data.id).shadowRoot.getElementById("text");
                    content.value = data.val;
                }
                if(data.id == "LabelText"){
                   ue4("textinput", data); 
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
                            event: "analytics.degree",
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
                            event: "analytics.closeness",
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
                            event: "analytics.eigenvector",
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
                            id: "analyticsClusteringcoefficientRun",
                            event: "analytics.clustering_coeff",
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

            case "enrichment":{
                if (data.id == "init") {
                    $("#enrichment-colors").css('display', 'none');
                    $("#enrichment-note-result").css('display', 'none');
                    $("#enrichment-note-features").css('display', 'none');
                    if (data.valHideNote == false) { $("#enrichment-note-features").css('display', 'block'); }

                    let button_container = document.getElementById("enrichment-query").shadowRoot.getElementById("box");
                    $(button_container).empty()
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

                    let targetName = "enrichment-container";
                    let targetContainer = document.getElementById(targetName);
                    let user = data.usr;

                    if (!data["valPlot"]){
                        targetContainer.innerHTML = "";
                        return;
                    }
                    let plot_data = JSON.parse(data["valPlot"]);
                    let payload = data.valPayload


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
                break;
            }
            case "community_detection": {
                // clear current buttons
                var container = $("#analyticsModCommunityGroups");
                container.empty();

                // create buttons with colors
                if (!data.data){return;}

                data.data.forEach((entry, idx)=>{
                    if (idx === 0){return;}
                    container.append(`<mc-button id = "button ${entry[0]}" val="${entry[0]}" name="C: ${entry[0]}" w="114" fn="add_community_to_clipboard" color="${rgbToHex(entry[1][0], entry[1][1], entry[1][2])}"></mc-button>`);
                });
                break;
            }
            case "legend_scene_display":{
                if (data.has_scenes === true) {
                    $("#legend-scene-description-container").css('display', 'block');
                    $("#legend-scene-description-element").html("SCENE : : " + data.text)
                }
                else {
                    $("#legend-scene-description-container").css('display', 'none');
                    $("#legend-scene-description-element").html("")
                }
                
            }
        }
    });



});


//----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function nodeInfoFormatValue(val) {
    // Renders a single node-attribute value as readable HTML, recursing into
    // nested arrays/objects instead of dumping raw JSON.
    if (val === null || val === undefined || val === "") {
        return '<span class="nodeinfo-empty">&mdash;</span>';
    }

    if (Array.isArray(val)) {
        if (val.length === 0) {
            return '<span class="nodeinfo-empty">&mdash;</span>';
        }
        var isPrimitiveList = val.every(function (v) {
            return v === null || typeof v !== "object";
        });
        if (isPrimitiveList) {
            return val.map(function (v) {
                return '<span class="nodeinfo-chip">' + escapeHtml(v) + '</span>';
            }).join("");
        }
        // array of objects -> render each entry as its own nested table
        return val.map(function (item, i) {
            return '<div class="nodeinfo-nested"><div class="nodeinfo-nested-title">[' + i + ']</div>'
                + nodeInfoFormatValue(item) + '</div>';
        }).join("");
    }

    if (typeof val === "object") {
        return nodeInfoBuildTable(val);
    }

    var str = String(val);
    if (/^https?:\/\//i.test(str)) {
        return '<a href="' + escapeHtml(str) + '" target="_blank" rel="noopener">' + escapeHtml(str) + '</a>';
    }
    return escapeHtml(str);
}

function nodeInfoBuildTable(obj) {
    var rows = Object.keys(obj).map(function (key) {
        return '<tr><td class="nodeinfo-key">' + escapeHtml(key) + '</td><td class="nodeinfo-val">'
            + nodeInfoFormatValue(obj[key]) + '</td></tr>';
    }).join("");
    return '<table class="nodeinfo-table">' + rows + '</table>';
}

function renderNodeInfoHTML(data) {
    // Formats the raw node-attribute object from the "node" socket event
    // into a readable key/value table instead of a raw JSON dump.
    if (!data || typeof data !== "object") {
        return '<span class="nodeinfo-empty">No data</span>';
    }
    return nodeInfoBuildTable(data);
}

function rgbToHex(red, green, blue) {
    const rgb = (red << 16) | (green << 8) | (blue << 0);
    return '#' + (0x1000000 + rgb).toString(16).slice(1);
}

function removeAllChildNodes(parent) {
    if (parent) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild);
        }
    }

}

// Clears UI state left over from the previously active project (search
// results, node/connections info, label suggestions, ...) - node ids and
// attributes are never comparable across projects, so anything keyed by
// them needs to be wiped whenever the project changes, not just re-fetched.
// Called from the "project" case below (project switch broadcast).
function clearProjectDependentPanels() {
    // node search (mNodesearch.html)
    if (document.getElementById("scrollbox2")) {
        removeAllChildNodes(document.getElementById("scrollbox2").shadowRoot.getElementById("box"));
    }
    if (document.getElementById("searchcount")) {
        document.getElementById("searchcount").innerHTML = "[-]";
    }
    if (document.getElementById("search")) {
        document.getElementById("search").shadowRoot.getElementById("text").value = "";
    }

    // node info (mNodeinfo.html)
    if (document.getElementById("nodeL2")) {
        document.getElementById("nodeL2").innerHTML = "";
    }
    if (document.getElementById("nodecount")) {
        document.getElementById("nodecount").innerHTML = "[-]";
    }
    if (document.getElementById("nodeRawdata")) {
        document.getElementById("nodeRawdata").innerHTML = "";
    }

    // connections (mConnections.html)
    if (document.getElementById("linkL2")) {
        document.getElementById("linkL2").innerHTML = "";
    }
    if (document.getElementById("plotly2js")) {
        document.getElementById("plotly2js").innerHTML = "";
    }
    if (document.getElementById("scrollbox3")) {
        removeAllChildNodes(document.getElementById("scrollbox3").shadowRoot.getElementById("box"));
    }

    // selections (mSelections.html)
    if (document.getElementById("scrollbox1")) {
        removeAllChildNodes(document.getElementById("scrollbox1").shadowRoot.getElementById("box"));
    }

    // label suggestions (mNodePainter.html / mClipboard.html)
    ["labelSuggestBox", "labelSuggestBoxCb"].forEach(function (boxId) {
        var box = document.getElementById(boxId);
        if (box) { removeAllChildNodes(box.shadowRoot.getElementById("box")); }
    });
}

function clearContainer(container){
    
}

function settextscroll(id, val) {
    console.log(id)
    var box = document.getElementById(id).shadowRoot.getElementById("box");
    $(box).scrollTop(val[0]);
    $(box).scrollLeft(val[1]);
}

function makeButton(parent, id, text) {
    var r = $('<input/>').attr({ type: "button", id: id, value: text });
    $(parent).append(r);
}


function removeOptions(selectElement) {
    var i, L = selectElement.options.length - 1;
    for (i = L; i >= 0; i--) {
        selectElement.remove(i);
    }
}

function log2HTML(logObj) {
    let obj = document.createElement('div');
    obj.style.margin = "3px";

    if (logObj.type == "log") {
        obj.innerHTML = `Log : : <span style="font-size:16px; font-weight:bold; color:rgb(200,200,200);">${logObj.msg}</span>`;
    }
    if (logObj.type == "warning") {
        obj.style.color = "rgb(250,0,0)";
        obj.innerHTML = `Warning : : <span style="font-size:16px; font-weight:bold; color:rgb(200,200,200);">${logObj.msg}</span>`;
    }
    return obj;
}

function handleLayoutExistsDisplay(exists) {
    // function to handle rerun and save button display in front end
    // exists: bool, if True: btns are displayed, false: btns are hidden
    // called on layout tab switch, layout run, init
    let layoutExistsBtns = document.getElementsByClassName("layoutExists");
    if (exists === true) {
        Array.prototype.forEach.call(layoutExistsBtns, function(element) {
            element.style.display = "inline-block";
        });
    } else {
        Array.prototype.forEach.call(layoutExistsBtns, function(element) {
            element.style.display = "none";
        });
    }
}
