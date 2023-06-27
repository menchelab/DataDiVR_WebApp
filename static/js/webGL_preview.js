        var layouts = [];
        var actLayout = 0;
        var layoutsl = [];
        var layoutsRGB = [];
        var nodesTempRGB = [];
        var actLayoutRGB = 0;
        var links = [];
        var actLinks = 0;
        var linksRGB = [];
        var linksRGBTemp = [];
        var actLinksRGB = 0;
        //var pfile = {"val":{"name":"AUToCOre","layouts":["01-Autocore_globalXYZ","02-Autocore_mix_globalclusterXYZ","03-Autocore_clusterfeaturesXYZ"],"layoutsRGB":["01-Autocore_globalRGB","02-Autocore_mix_globalclusterRGB","03-Autocore_clusterfeaturesRGB"],"links":["Autocore_linksXYZ"],"linksRGB":["Autocore_linksRGB"]},"fn":"project"};
        var pfile = {};
        var mesh, renderer, scene, camera, controls;
        //var data = JSON.parse('{"nodes":[{"p":[0.5,0.5,0.5],"c":[128,128,128,128],"n":"TEST1"},{"p":[0.7,0.7,0.7],"c":[ 0,128,128,128],"n":"TEST2"},{"p":[0.2,0.2,0.2],"c":[128,0,128,128],"n":"TEST3"}],"links":[{"id":0,"s":0,"e":1,"c":[0,128,128,128]},{"id":1,"s":1,"e":2,"c":[0,128,128,128]},{"id":2,"s":2,"e":1,"c":[0,128,128,128]}]}');
        var data = {};
        var scale = 20;
        const nscale = .02;
        var nodemeshes = [];
        var linkmeshes = []
        var indexsphere;
        var labels = [];
        var children = [];
        var selNode = 0;
        var initialized = false; //block incoming socket messages from drawing the network multiple times on startup
        
        
        function init() {
            // renderer
            //document.getElementById("size").innerHTML = data["links"].length + " LINKS<br>" ; //+ pdata["labels"][0] + " NODES<br>
            renderer = new THREE.WebGLRenderer();
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            // scene
            scene = new THREE.Scene();
            // camera
            camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 10000);
            camera.position.set(20, 0, 0);
            camera.layers.enable(1);// camera shows layers 0 + 1, only 0 (cubes) gets racasted
            raycaster = new THREE.Raycaster();
            mouse = new THREE.Vector2()
            // controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.addEventListener('change', function() {
                onCameraChange();
            });
            // axes
            scene.add(new THREE.AxesHelper(20));
            const geometry = new THREE.SphereGeometry(nscale, 32, 16);
            var material = new THREE.MeshBasicMaterial({
                color: 0xFFFFFF,
                transparent: true,
                opacity: 0.4,
            });
            const sphere = new THREE.Mesh(geometry, material);
            sphere.layers.set(1);
            indexsphere = sphere;
            scene.add(sphere);
            /*
            // ambient
            scene.add( new THREE.AmbientLight( 0x222222 ) );
            
            // light
            var light = new THREE.DirectionalLight( 0xffffff, 1 );
            light.position.set( 20,20, 0 );
            scene.add( light );
            
            */
           // makeNetwork(data);
        
            // camera rotation-> https://jsfiddle.net/8kn4qrz0/
            window.addEventListener('resize', onWindowResize, false);
            renderer.domElement.addEventListener('click', onClick, false);
        }
        function RGB2HTML(red, green, blue) {
                var decColor = 0x1000000 + blue + 0x100 * green + 0x10000 * red;
                return '#' + decColor.toString(16).substr(1);
        }

        function RGBA2HTML(rgba) {
            var r = rgba[0].toString(16).padStart(2, '0');
            var g = rgba[1].toString(16).padStart(2, '0');
            var b = rgba[2].toString(16).padStart(2, '0');
            var a = Math.round(rgba[3] / 255 * 100) / 100;
            a = Math.round(a * 255).toString(16).padStart(2, '0');
            return "#" + r + g + b + a;
          }
        
        function getPosition(index){
            var i = index * 4;
            var scene = actLayout;
            var positionX = (layouts[scene][i]*255 + layoutsl[scene][i])/ 65536 - 0.5;
            var positionY = (layouts[scene][i+1]*255 + layoutsl[scene][i+1])/ 65536 - 0.5;
            var positionZ = (layouts[scene][i+2]*255 + layoutsl[scene][i+2])/ 65536 - 0.5;
            var position = [positionX, positionY, positionZ];
            return position;
        }

        function getNColor(index){
            var i = index * 4;
            var scene = actLayoutRGB;
            var color = [layoutsRGB[scene][i], layoutsRGB[scene][i+1], layoutsRGB[scene][i+2]];
            return color;
        }
        
        function getLColor(index){
            var i = index * 4;
            var scene = actLinksRGB;
            var color = [linksRGB[scene][i], linksRGB[scene][i+1], linksRGB[scene][i+2]];
            return color;
        }
        
        function getLink(index){
            var i = index * 8;
            var scene = actLinks;
            var link = {};
            link["start"] = links[scene][i] + links[scene][i+1]*128 + links[scene][i+2]*16384;
            link["end"] = links[scene][i+4] + links[scene][i+5]*128 + links[scene][i+6]*16384; 
            //console.log("created link from " + link["start"] + " to " + link["end"]); 
            return link;
        }
        function updateNodeColors(data){

            for (let i = 0; i < (nodemeshes.length); i++){
                color = [data[i*4], data[i*4+1], data[i*4+2]];
                nodemeshes[i].material.color.set(RGB2HTML(color[0],color[1],color[2]))  
            }
            console.log("node colors updated")
        }

        function updateLinkColors(data){
            //console.log(linkmeshes);
            for (let i = 0; i < (linkmeshes.length); i++){
                color = [data[i*4], data[i*4+1], data[i*4+2]];
                linkmeshes[i].material.color.set(RGB2HTML(color[0], color[1], color[2]));
            }
            //console.log(linkmeshes);
            console.log("link colors updated")
        }

        async function updateLayoutTemp(path_low, path_hi){
            function getPositionFromTemp(index, temp_low, temp_hi){
                var i = index * 4;
                var positionX = (temp_hi[i]*255 + temp_low[i]) / 65536 - 0.5;
                var positionY = (temp_hi[i+1]*255 + temp_low[i+1]) / 65536 - 0.5;
                var positionZ = (temp_hi[i+2]*255 + temp_low[i+2]) / 65536 - 0.5;
                var position = [positionX, positionY, positionZ];
                return position;
            }

            if (initialized){
                let layout_hi = await DownloadImage(path_hi);
                let layout_low = await DownloadImage(path_low);


                //delete everything but sphere  
                console.log("update network");      
                const n = scene.children.length - 1; 
                for (var i = n; i > -1; i--) {
                    if (scene.children[i] != indexsphere){
                        scene.remove(scene.children[i]);
                    }    
                }
                
                const elements = document.getElementsByClassName("label");
                while(elements.length > 0){
                    elements[0].parentNode.removeChild(elements[0]);
                }
                
                nodemeshes=[];
                linkmeshes = []
                labels=[];
            
                // make new nodes from temp files
 
 
                for (let i = 0; i < ( pfile["nodecount"]+ pfile["labelcount"]); i++){
                    if (i<10000){

                    const ngeometry = new THREE.BoxGeometry(nscale, nscale, nscale);
                    var color = getNColor(i);
                    const nmaterial = new THREE.MeshBasicMaterial({ color: RGB2HTML(color[0], color[1], color[2])});//"rgb(155, 102, 102)" 
                    const cube = new THREE.Mesh(ngeometry, nmaterial);
                    cube.name = i;//;
                    cube.layers.set(0);
                    nodemeshes.push(cube);

                    scene.add(cube);
                    var nodepos = getPositionFromTemp(i, layout_low, layout_hi);
                    cube.position.set((nodepos[1] * -1) * scale , nodepos[2] * scale, nodepos[0] * scale,); //0x00ff00
            
                    // MAKE LABELS
                        if (i >= pfile["nodecount"]){

                            var name = pfile["selections"][(i - pfile["nodecount"])]["name"];
                        
                            $('body').append('<div id="lab'+i+'"class="label" text="label"style="z-index: 1; position: absolute; top: 389px; left: 271px; margin-left: 10px; font-size: 20px;">'+ name +'</div>');
                            labels.push("lab" + i);
                        }
                    
                    }
                }
                    
                
                // Draw Links
                maxl = 10000;
                if (pfile["linkcount"] > maxl) {
                document.getElementById("warning").innerHTML = "TOO MANY LINKS<br>FOR PREVIEW";
                }
                else{maxl = pfile["linkcount"];}
                count = 0;
                for (let l = 0; l < maxl; l++) {
            
                        var link = getLink(l);
                        var color = getLColor(l);
                        const material1 = new THREE.LineBasicMaterial({ color: RGB2HTML(color[0], color[1], color[2]), transparent: true, opacity: 0.2 });
                        const points = [];
                        const start = link["start"];
                        const end = link["end"];
                        
                        points.push(nodemeshes[start].position);
                        points.push(nodemeshes[end].position);
                        const geometry1 = new THREE.BufferGeometry().setFromPoints(points);
                        const line = new THREE.Line(geometry1, material1);
                        line.layers.set(1);
                        line.linewidth
                        line.name = "line"
                        scene.add(line);
                        linkmeshes.push(line)
                        count = l
                }
            }   
        }


        function makeNetwork(){
            if (initialized){
                //delete everything but sphere  
                console.log("construct network");      
                const n = scene.children.length - 1; 
                for (var i = n; i > -1; i--) {
                    if (scene.children[i] != indexsphere){
                        scene.remove(scene.children[i]);
                    }    
                }
                
                const elements = document.getElementsByClassName("label");
                while(elements.length > 0){
                    elements[0].parentNode.removeChild(elements[0]);
                }
                
                nodemeshes=[];
                linkmeshes = []
                labels=[];
            
                // MAKE NODES
 
 
                for (let i = 0; i < ( pfile["nodecount"]+ pfile["labelcount"]); i++){
                    if (i<10000){

                    const ngeometry = new THREE.BoxGeometry(nscale, nscale, nscale);
                    var color = getNColor(i);
                    const nmaterial = new THREE.MeshBasicMaterial({ color: RGB2HTML(color[0], color[1], color[2])});//"rgb(155, 102, 102)" 
                    const cube = new THREE.Mesh(ngeometry, nmaterial);
                    cube.name = i;//;
                    cube.layers.set(0);
                    nodemeshes.push(cube);
                    //console.log(data['nodes'][i]["n"]);
                    scene.add(cube);
                    var nodepos = getPosition(i);
                    cube.position.set((nodepos[1] * -1) * scale , nodepos[2] * scale, nodepos[0] * scale,); //0x00ff00
            
                    // MAKE LABELS
                        if (i >= pfile["nodecount"]){

                            
                            // match label with layout to show only for specific layout
                            var selected_layout_index = getIndexforwardstep(pfile["layouts"].length);
                            var selected_layout = pfile["layouts"][selected_layout_index];

                            var layoutname_pfile = pfile["selections"][0]["layoutname"]+"XYZ"
                            //console.log("C_DEBUG selected_layout = ",selected_layout);
                            //console.log("C_DEBUG layoutname = ", layoutname_pfile);

                            if (selected_layout === layoutname_pfile) {

                                var name = pfile["selections"][(i - pfile["nodecount"])]["name"];
                                //console.log("C_DEBUG name = ", name);

                                $('body').append('<div id="lab'+i+'"class="label" text="label"style="z-index: 1; position: absolute; top: 389px; left: 271px; margin-left: 10px; font-size: 20px;">'+ name +'</div>');
                                labels.push("lab" + i);
                                //break; // If you want to stop the iteration after finding the first match
                    
                            }
              
                        }
                    
                    }

                    //<div id="label" style="z-index: 2; position: absolute; top: 389px; left: 271px; color: white; margin-left: 10px; font-size: 30px;"></div>
                }
                    
                
                // Draw Links
                maxl = 10000;
                if (pfile["linkcount"] > maxl) {
                document.getElementById("warning").innerHTML = "TOO MANY LINKS<br>FOR PREVIEW";
                }
                else{maxl = pfile["linkcount"];}
                count = 0;
                for (let l = 0; l < maxl; l++) {
            
                        var link = getLink(l);
                        var color = getLColor(l);
                        const material1 = new THREE.LineBasicMaterial({ color: RGB2HTML(color[0], color[1], color[2]), transparent: true, opacity: 0.2 });
                        const points = [];
                        const start = link["start"];
                        const end = link["end"];
                        

                        //children[start].push(end);
                        //children[end].push(start);

                        points.push(nodemeshes[start].position);
                        points.push(nodemeshes[end].position);
                        const geometry1 = new THREE.BufferGeometry().setFromPoints(points);
                        const line = new THREE.Line(geometry1, material1);
                        line.layers.set(1);
                        line.linewidth
                        line.name = "line"
                        scene.add(line);
                        linkmeshes.push(line)
                        count = l
                    //}
                }
               
                //console.log(linkmeshes);
            }   
        }

        function onClick() {
            event.preventDefault();
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            //console.log("clc")
            raycaster.setFromCamera(mouse, camera);
            var intersects = raycaster.intersectObject(scene, true);
            if (intersects.length > 0) {
                var object = null
                for (var i = 0; i < intersects.length; i++){
                    if (intersects[i].object.name){
                        object = intersects[0].object;
                    }
                     
                    //console.log(intersects[i].object.name);
                }
                if (object != null){
                    indexsphere.position.set(object.position["x"], object.position["y"], object.position["z"]);
                    
                    
                    
                    socket.emit('ex', { msg: "none", id: "none",val: object.name,  fn: 'node'});
                }   
        
            }
        }
        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        function rigth() {
            camera.position.set(0, 0, 20);
            camera.lookAt(0, 0, 0);
            camera.rotation.z += Math.PI / 2
            camera.updateProjectionMatrix();
        }
        function nodescale(scale) {
            //console.log(scale);
            for (let l = 0; l < nodemeshes.length; l++) {
                nodemeshes[l].scale.set(scale, scale, scale);
            }
            indexsphere.scale.set(scale + 2, scale + 2, scale + 2);
            //render();
        }
        // this is called from connect SocketIO whenever any nodebutton is pressed
        function setUserLabelPos(index, name) {
                selNode = index;
                var object = nodemeshes[index];
                var proj = toScreenPosition(nodemeshes[index], camera);
                document.getElementById("label").innerHTML = name;
                document.getElementById("label").style.left = Math.floor(proj.x) + 'px';
                document.getElementById("label").style.top = Math.floor(proj.y) + 'px';
        
                indexsphere.position.set(object.position["x"], object.position["y"], object.position["z"]);  
                //console.log(name);
        }
        function updateUserLabelPos(index) {
            if (nodemeshes.length > index ){
                if (document.getElementById("label")){
                    var proj = toScreenPosition(nodemeshes[index], camera);
                    document.getElementById("label").style.left = Math.floor(proj.x) + 'px';
                    document.getElementById("label").style.top = Math.floor(proj.y) + 'px';
                }

            }   
        }
        function setLabelPos() {
            var offset = pfile["nodecount"]
            for (let l = 0; l <  labels.length; l++) {       
                lname = labels[l];
                //console.log(lname);
                var proj = toScreenPosition(nodemeshes[l + offset], camera);
                document.getElementById(lname).style.left = Math.floor(proj.x) + 'px';
                document.getElementById(lname).style.top = Math.floor(proj.y) + 'px';
                document.getElementById(lname).style.color = RGB2HTML(255,255,255)
                //document.getElementById(lname).style.color = RGB2HTML(Math.floor(nodemeshes[l + offset].material.color["r"] * 255), Math.floor(nodemeshes[l + offset].material.color["g"] * 255), Math.floor(nodemeshes[l + offset].material.color["b"] * 255),255)
            }
        }
        function onCameraChange() {
            updateUserLabelPos(selNode);
            if(pfile['labelcount'] > 0){
                //console.log("haslabels");
                setLabelPos(); 
            }else{
                //console.log("hasNolabels");
            }
        }
        function toScreenPosition(obj, camera) {
            if(obj != null && camera != null){
                camera.updateMatrixWorld();
                var vector = new THREE.Vector3();
                // TODO: need to update this when resize window
                var widthHalf = 0.5 * window.innerWidth;
                var heightHalf = 0.5 * window.innerHeight;
                obj.updateMatrixWorld();
                vector.setFromMatrixPosition(obj.matrixWorld);
                vector.project(camera);
                vector.x = (vector.x * widthHalf) + widthHalf;
                vector.y = - (vector.y * heightHalf) + heightHalf;
                return {
                    x: vector.x,
                    y: vector.y
                };
                }
        }
        
        
        
        
        function DownloadImage(url) {
            
            return new Promise(function (resolve, reject) {
                //  https://stackoverflow.com/questions/48969495/in-javascript-how-do-i-should-i-use-async-await-with-xmlhttprequest  
                var oReq = new XMLHttpRequest();
                oReq.open("GET", url, true);
                oReq.responseType = "arraybuffer";
                
                oReq.onload = function (oEvent) {
        
                    var arrayBuffer = oReq.response; // Note: not oReq.responseText
                    var binaryString = '';
                    
                    if (arrayBuffer) {
                        var byteArray = new Uint8Array(arrayBuffer);
        
                        for (var i = 0; i < byteArray.byteLength; i++) {
                            binaryString += String.fromCharCode(byteArray[i]); //extracting the bytes
                        }
                        var base64 = window.btoa(binaryString); //creating base64 string
                        str = "data:image/png;base64," + base64; //creating a base64 uri
                        var image = new Image();
                        image.src = str;
                        image.onload = function() {
                            var canvas = document.createElement("canvas");
                            canvas.width = image.width;
                            canvas.height = image.height;
                            
                            var ctx = canvas.getContext('2d');
                            ctx.drawImage(image, 0, 0);
                            var imageData = ctx.getImageData(0, 0, image.width, image.height);
                            resolve(imageData["data"]);
                        }
                        //document.getElementById(parent).appendChild(canvas);
                    }
                            
                };
        
                oReq.onerror = function () {
                    reject({
                        status: this.status,
                        statusText: xhr.statusText
                    });
                };
        
                oReq.send(null);
            });
        }
        
        function clearProject(){
            layouts = [];
            actLayout = 0;
            layoutsl = [];
            layoutsRGB = [];
            actLayoutRGB = 0;
            links = [];
            actLinks = 0;
            linksRGB = [];
            actLinksRGB = 0;

        }

        

        async function downloadProjectTextures() {
            clearProject();
            console.log("downloading project maps " + pfile["name"]);
            
            for (let index = 0; index < pfile["layouts"].length; index++) {
                var path ="/static/projects/"  + pfile["name"] + "/layouts/" +  pfile["layouts"][index] + ".bmp";
                var pathl ="/static/projects/"  + pfile["name"] + "/layoutsl/" +  pfile["layouts"][index] + "l.bmp";
                layouts.push(await DownloadImage(path));
                layoutsl.push(await DownloadImage(pathl));
            }
        
            for (let index = 0; index < pfile["layoutsRGB"].length; index++) {
                var path ="/static/projects/"  + pfile["name"] + "/layoutsRGB/" +  pfile["layoutsRGB"][index] + ".png";
                layoutsRGB.push(await DownloadImage(path));
            }
        
            for (let index = 0; index < pfile["links"].length; index++) {
                var path ="/static/projects/"  + pfile["name"] + "/links/" +  pfile["links"][index] + ".bmp";
                links.push(await DownloadImage(path));
                
            }
            

            for (let index = 0; index < pfile["linksRGB"].length; index++) {
                var path ="/static/projects/"  + pfile["name"] + "/linksRGB/" +  pfile["linksRGB"][index] + ".png";
                linksRGB.push(await DownloadImage(path));
            }
            
            //makeNetwork();
            var text = '{"id":"x", "success": "true", "fn": "projectLoaded"}';
            var out = JSON.parse(text);
            out['usr'] = uid;
            socket.emit('ex', out);
        
        }
        
        async function downloadTempTexture(path, channel) {
            switch (channel){
                case "nodeRGB":
                    let nodesTempRGB = await DownloadImage(path);
                    console.log(nodesTempRGB[0],nodesTempRGB[1],nodesTempRGB[2]);
                    updateNodeColors(nodesTempRGB);
                    break;
                case "linkRGB":
                    let linksTempRGB = await DownloadImage(path);
                    console.log(linksTempRGB[0], linksTempRGB[1], linksTempRGB[2]);
                    updateLinkColors(linksTempRGB);
                    break;
            }
        }
        
        document.addEventListener("DOMContentLoaded", function () {
            init();
            animate();
            rigth();
            //doAjaxThings(pfile); //is called from connect socketio
            // create and manipulate your DOM here. doAjaxThings() will run asynchronously and not block your DOM rendering
        
        });
        
        