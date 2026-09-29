// --- MOCK VR CLIENT (dev only) ---
// Open /main?mockvr to get a floating panel that stands in for the Unreal client:
//  - wraps ue4() and logs everything the web app would send to UE
//  - reacts like UE would: loads the project's layout/color textures, follows the
//    layoutsDD/layoutsRGBDD dropdowns, the brush size slider and updateTempTex
//  - a 2D projection of the node layout acts as the VR paint brush: it calls the
//    real ue.interface.paintnodesADD/SUB/CLEAR/SAVE + speech callbacks, so the whole
//    UE -> socket -> flask -> texture -> updateTempTex -> UE round trip is exercised
// Loaded by main.html only when the "mockvr" query parameter is present.

(function() {
    if (!new URLSearchParams(location.search).has("mockvr")) { return; }

    var state = {
        pfile: null,
        layoutIdx: 0,
        colorIdx: 0,
        positions: null,   // Float32Array [x,y,z,...] per node
        colors: null,      // Uint8ClampedArray RGBA per node (current nodeRGB texture)
        screen: null,      // Float32Array [sx,sy,...] per node
        axes: [0, 1],      // projected axes (0=x, 1=y, 2=z)
        brush: 500,        // slider-brush_size value, 0..1000
        brushColor: "rgba(128,0,255,1)",
        paintedCount: 0,
        sendAsString: true, // UE hands data over as JSON strings
        pending: { ADD: new Set(), SUB: new Set() },
        mouse: null,
        painting: null
    };

    // ---------- panel ----------
    var css = "\
#mockvr{position:fixed;right:16px;top:16px;width:440px;z-index:100000;background:#141414;color:#ddd;border:2px solid #7f3fff;border-radius:8px;font:12px/1.4 monospace;box-shadow:0 4px 24px #000a}\
#mockvr header{cursor:move;padding:6px 10px;background:#7f3fff;color:#fff;font-weight:bold;display:flex;justify-content:space-between;align-items:center}\
#mockvr header button{background:none;border:0;color:#fff;cursor:pointer;font:inherit}\
#mockvr .body{padding:8px}\
#mockvr canvas{display:block;background:#000;border:1px solid #333;cursor:none;width:420px;height:420px}\
#mockvr .row{display:flex;gap:4px;flex-wrap:wrap;margin:6px 0;align-items:center}\
#mockvr button.b{background:#2a2a2a;color:#ddd;border:1px solid #555;border-radius:4px;padding:3px 8px;cursor:pointer;font:inherit}\
#mockvr button.b:hover{border-color:#7f3fff}\
#mockvr input[type=text]{background:#222;color:#ddd;border:1px solid #555;border-radius:4px;padding:3px 6px;font:inherit;flex:1;min-width:0}\
#mockvr .log{height:150px;overflow:auto;background:#0b0b0b;border:1px solid #333;padding:4px;white-space:pre-wrap;word-break:break-all}\
#mockvr .log div{border-bottom:1px solid #1d1d1d}\
#mockvr .log .hl{color:#c9a7ff}\
#mockvr .log .out{color:#7fd4ff}\
#mockvr .stat{color:#aaa}";
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var panel = document.createElement("div");
    panel.id = "mockvr";
    panel.innerHTML = '\
<header><span>MOCK VR CLIENT</span><span><button id="mvrMin" title="collapse">_</button></span></header>\
<div class="body">\
  <div class="stat" id="mvrStat">waiting for project...</div>\
  <canvas id="mvrCanvas" width="420" height="420"></canvas>\
  <div class="stat">left drag: paint (ADD) &middot; right/shift drag: erase (SUB) &middot; wheel: brush size</div>\
  <div class="row">\
    <button class="b" id="mvrAxes">view: XY</button>\
    <button class="b" id="mvrClear">paintnodesCLEAR</button>\
    <button class="b" id="mvrRandom">ADD 20 random</button>\
    <button class="b" id="mvrFormat">data: JSON string</button>\
  </div>\
  <div class="row">\
    <input type="text" id="mvrName" placeholder="selection name">\
    <button class="b" id="mvrSave">paintnodesSAVE</button>\
    <button class="b" id="mvrSpeech" title="send the name like the VR keyboard (ue.interface.speech)">VR keyboard</button>\
  </div>\
  <div class="row"><span class="stat">UE log</span> <span class="stat" style="opacity:.6">(&rarr; = web&rarr;UE via ue4(), &larr; = UE&rarr;web callback)</span>\
    <button class="b" id="mvrLogClear" style="margin-left:auto">clear log</button></div>\
  <div class="log" id="mvrLog"></div>\
</div>';
    document.body.appendChild(panel);

    var $ = function(id) { return document.getElementById(id); };
    var canvas = $("mvrCanvas");
    var ctx = canvas.getContext("2d");

    // drag the panel by its header
    (function() {
        var header = panel.querySelector("header");
        var start = null;
        header.addEventListener("mousedown", function(e) {
            start = { x: e.clientX, y: e.clientY, left: panel.offsetLeft, top: panel.offsetTop };
            e.preventDefault();
        });
        window.addEventListener("mousemove", function(e) {
            if (!start) return;
            panel.style.left = (start.left + e.clientX - start.x) + "px";
            panel.style.top = (start.top + e.clientY - start.y) + "px";
            panel.style.right = "auto";
        });
        window.addEventListener("mouseup", function() { start = null; });
        $("mvrMin").addEventListener("click", function() {
            var body = panel.querySelector(".body");
            body.style.display = body.style.display === "none" ? "" : "none";
        });
    })();

    // ---------- log ----------
    function log(dir, fn, payload) {
        var box = $("mvrLog");
        var line = document.createElement("div");
        var text = payload === undefined ? "" : (typeof payload === "string" ? payload : JSON.stringify(payload));
        if (text.length > 220) { text = text.slice(0, 220) + "..."; }
        line.textContent = (dir === "in" ? "← " : "→ ") + fn + "  " + text;
        if (dir === "in") { line.className = "out"; }
        else if (/paint|saveNodeSelection|updateTempTex|sli/.test(fn)) { line.className = "hl"; }
        box.appendChild(line);
        while (box.childNodes.length > 200) { box.removeChild(box.firstChild); }
        box.scrollTop = box.scrollHeight;
    }
    $("mvrLogClear").addEventListener("click", function() { $("mvrLog").innerHTML = ""; });

    // UE -> web: call the real ue.interface callback (defined in connect_socketIO_main.js)
    function callUE(name, data) {
        log("in", "ue.interface." + name, data);
        if (typeof ue.interface[name] !== "function") {
            log("in", "!! ue.interface." + name + " is not defined");
            return;
        }
        ue.interface[name](data);
    }

    // ---------- textures ----------
    function loadImageData(url) {
        return fetch(url + (url.indexOf("?") < 0 ? "?" : "&") + "mockvr=" + Date.now(), { cache: "no-store" })
            .then(function(r) { if (!r.ok) throw new Error(r.status + " " + url); return r.blob(); })
            .then(function(blob) { return createImageBitmap(blob); })
            .then(function(bmp) {
                var c = document.createElement("canvas");
                c.width = bmp.width; c.height = bmp.height;
                var cx = c.getContext("2d");
                cx.drawImage(bmp, 0, 0);
                return cx.getImageData(0, 0, bmp.width, bmp.height).data;
            });
    }

    function nodeCount() {
        return state.pfile ? (state.pfile.nodecount || 0) : 0;
    }

    function loadLayout() {
        var pf = state.pfile;
        if (!pf || !pf.layouts || !pf.layouts.length) return Promise.resolve();
        var name = pf.layouts[Math.min(state.layoutIdx, pf.layouts.length - 1)];
        return Promise.all([
            loadImageData("/static/projects/" + pf.name + "/layouts/" + name + ".bmp"),
            loadImageData("/static/projects/" + pf.name + "/layoutsl/" + name + "l.bmp")
        ]).then(function(res) {
            var hi = res[0], lo = res[1];
            var n = Math.min(nodeCount() || hi.length / 4, hi.length / 4);
            var pos = new Float32Array(n * 3);
            // same decoding as webGL_preview.js getPosition()
            for (var i = 0; i < n; i++) {
                for (var k = 0; k < 3; k++) {
                    pos[i * 3 + k] = (hi[i * 4 + k] * 255 + lo[i * 4 + k]) / 65536 - 0.5;
                }
            }
            state.positions = pos;
            project2D();
        });
    }

    function loadColors(url) {
        var pf = state.pfile;
        if (!url) {
            if (!pf || !pf.layoutsRGB || !pf.layoutsRGB.length) return Promise.resolve();
            url = "/static/projects/" + pf.name + "/layoutsRGB/" + pf.layoutsRGB[Math.min(state.colorIdx, pf.layoutsRGB.length - 1)] + ".png";
        }
        return loadImageData(url).then(function(data) { state.colors = data; draw(); });
    }

    function loadProject(pfile) {
        state.pfile = pfile;
        state.positions = null; state.colors = null;
        setStat();
        Promise.all([loadLayout(), loadColors()])
            .then(function() {
                // what UE does once its assets are in: tell the web app it's ready
                callUE("projectLoaded", "mock");
            })
            .catch(function(err) { log("in", "!! texture load failed: " + err); });
    }

    // ---------- projection / drawing ----------
    function project2D() {
        var pos = state.positions;
        if (!pos) return;
        var n = pos.length / 3, a = state.axes[0], b = state.axes[1];
        var minA = Infinity, maxA = -Infinity, minB = Infinity, maxB = -Infinity;
        for (var i = 0; i < n; i++) {
            var va = pos[i * 3 + a], vb = pos[i * 3 + b];
            if (va < minA) minA = va; if (va > maxA) maxA = va;
            if (vb < minB) minB = vb; if (vb > maxB) maxB = vb;
        }
        var pad = 12, size = canvas.width - 2 * pad;
        var scale = size / Math.max(maxA - minA, maxB - minB, 1e-6);
        var scr = new Float32Array(n * 2);
        for (var j = 0; j < n; j++) {
            scr[j * 2] = pad + (pos[j * 3 + a] - minA) * scale;
            scr[j * 2 + 1] = canvas.height - (pad + (pos[j * 3 + b] - minB) * scale);
        }
        state.screen = scr;
        draw();
    }

    function brushRadius() {
        return 3 + (state.brush / 1000) * 40;
    }

    function draw() {
        ctx.fillStyle = "#000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        var scr = state.screen, col = state.colors;
        if (scr) {
            var n = scr.length / 2;
            for (var i = 0; i < n; i++) {
                if (col && i * 4 + 3 < col.length) {
                    ctx.fillStyle = "rgba(" + col[i * 4] + "," + col[i * 4 + 1] + "," + col[i * 4 + 2] + "," + Math.max(col[i * 4 + 3] / 255, 0.25) + ")";
                } else {
                    ctx.fillStyle = "#888";
                }
                ctx.fillRect(scr[i * 2] - 1, scr[i * 2 + 1] - 1, 2, 2);
            }
        }
        if (state.mouse) {
            ctx.beginPath();
            ctx.arc(state.mouse.x, state.mouse.y, brushRadius(), 0, Math.PI * 2);
            ctx.strokeStyle = state.painting === "SUB" ? "#fff" : state.brushColor;
            ctx.lineWidth = 2;
            ctx.setLineDash(state.painting === "SUB" ? [4, 3] : []);
            ctx.stroke();
            ctx.setLineDash([]);
        }
    }

    var drawQueued = false;
    function queueDraw() {
        if (drawQueued) return;
        drawQueued = true;
        requestAnimationFrame(function() { drawQueued = false; draw(); });
    }

    function setStat() {
        var pf = state.pfile;
        $("mvrStat").textContent = pf
            ? pf.name + " · " + (pf.nodecount || "?") + " nodes · layout " + state.layoutIdx + " · color " + state.colorIdx +
              " · brush " + state.brush + " · painted " + state.paintedCount
            : "waiting for project...";
    }

    // ---------- brush ----------
    function nodesUnderBrush(x, y) {
        var scr = state.screen, ids = [];
        if (!scr) return ids;
        var r2 = brushRadius() * brushRadius();
        for (var i = 0; i < scr.length / 2; i++) {
            var dx = scr[i * 2] - x, dy = scr[i * 2 + 1] - y;
            if (dx * dx + dy * dy <= r2) ids.push(i);
        }
        return ids;
    }

    function sendPaint(op, ids) {
        if (!ids.length) return;
        callUE(op === "ADD" ? "paintnodesADD" : "paintnodesSUB", state.sendAsString ? JSON.stringify(ids) : ids);
    }

    // throttle: collect ids while dragging, flush every 150 ms (each flush = one texture render on the server)
    setInterval(function() {
        ["ADD", "SUB"].forEach(function(op) {
            if (state.pending[op].size) {
                sendPaint(op, Array.from(state.pending[op]));
                state.pending[op].clear();
            }
        });
    }, 150);

    function mousePos(e) {
        var rect = canvas.getBoundingClientRect();
        return { x: (e.clientX - rect.left) * canvas.width / rect.width, y: (e.clientY - rect.top) * canvas.height / rect.height };
    }

    function stroke(e) {
        state.mouse = mousePos(e);
        if (state.painting) {
            nodesUnderBrush(state.mouse.x, state.mouse.y).forEach(function(id) { state.pending[state.painting].add(id); });
        }
        queueDraw();
    }

    canvas.addEventListener("contextmenu", function(e) { e.preventDefault(); });
    canvas.addEventListener("mousedown", function(e) {
        state.painting = (e.button === 2 || e.shiftKey) ? "SUB" : "ADD";
        stroke(e);
    });
    canvas.addEventListener("mousemove", stroke);
    window.addEventListener("mouseup", function() { state.painting = null; queueDraw(); });
    canvas.addEventListener("mouseleave", function() { state.mouse = null; queueDraw(); });
    canvas.addEventListener("wheel", function(e) {
        e.preventDefault();
        state.brush = Math.max(0, Math.min(1000, state.brush + (e.deltaY < 0 ? 50 : -50)));
        setStat(); queueDraw();
    }, { passive: false });
    // wheel only changes the local brush preview; release pushes it to the shared slider like UE would
    canvas.addEventListener("wheel", debounce(function() {
        if (typeof socket !== "undefined") {
            socket.emit("ex", { usr: uid, id: "slider-brush_size", fn: "sli", val: String(state.brush) });
        }
    }, 400));

    function debounce(fn, ms) {
        var t = null;
        return function() { clearTimeout(t); t = setTimeout(fn, ms); };
    }

    // ---------- buttons ----------
    var AXES = [[0, 1, "XY"], [0, 2, "XZ"], [2, 1, "ZY"]];
    var axesIdx = 0;
    $("mvrAxes").addEventListener("click", function() {
        axesIdx = (axesIdx + 1) % AXES.length;
        state.axes = [AXES[axesIdx][0], AXES[axesIdx][1]];
        this.textContent = "view: " + AXES[axesIdx][2];
        project2D();
    });
    $("mvrClear").addEventListener("click", function() { callUE("paintnodesCLEAR", ""); });
    $("mvrRandom").addEventListener("click", function() {
        var n = nodeCount(), ids = [];
        for (var i = 0; i < 20 && n > 0; i++) ids.push(Math.floor(Math.random() * n));
        sendPaint("ADD", ids);
    });
    $("mvrFormat").addEventListener("click", function() {
        state.sendAsString = !state.sendAsString;
        this.textContent = "data: " + (state.sendAsString ? "JSON string" : "array");
    });
    $("mvrSave").addEventListener("click", function() { callUE("paintnodesSAVE", $("mvrName").value); });
    $("mvrSpeech").addEventListener("click", function() {
        callUE("speech", JSON.stringify({ id: "paintSelName", text: $("mvrName").value }));
    });

    // ---------- web -> UE: wrap ue4() ----------
    function onUE(fn, data) {
        if (typeof data === "string") { try { data = JSON.parse(data); } catch (e) {} }
        if (!data || typeof data !== "object") return;

        switch (fn) {
            case "project":
                loadProject(data.val);
                break;
            case "dropdown":
                if (data.id === "layoutsDD" && data.sel !== undefined) {
                    state.layoutIdx = parseInt(data.sel) || 0; setStat(); loadLayout();
                } else if (data.id === "layoutsRGBDD" && data.sel !== undefined) {
                    state.colorIdx = parseInt(data.sel) || 0; setStat(); loadColors();
                }
                break;
            case "sli":
                if (data.id === "slider-brush_size") {
                    state.brush = parseInt(data.val) || 0; setStat(); queueDraw();
                }
                break;
            case "updateTempTex":
                (data.textures || []).forEach(function(t) {
                    if (t.channel === "nodeRGB") { loadColors("/" + t.path.replace(/^\//, "")); }
                });
                break;
            case "paintnodes":
                if (data.id === "paintnodesStatus") {
                    state.paintedCount = data.count;
                    if (data.color) {
                        state.brushColor = "rgba(" + data.color[0] + "," + data.color[1] + "," + data.color[2] + "," + Math.max(data.color[3] / 255, 0.4) + ")";
                    }
                    setStat(); queueDraw();
                }
                break;
        }
    }

    var realUE4 = window.ue4;
    window.ue4 = function(fn, data) {
        log("out", fn, data);
        try { onUE(fn, data); } catch (err) { console.error("mockVR:", err); }
        // in a normal browser the real broadcast only pushes a #hash - skip it to keep the URL clean
        if (realUE4 && isUE4) { realUE4(fn, data); }
    };

    // debug handle for the console / automated tests
    window.__mockVR = { state: state, callUE: callUE };

    // in case the project arrived before this script ran
    if (typeof pfile !== "undefined" && pfile && pfile.name) { loadProject(pfile); }

    draw();
})();
