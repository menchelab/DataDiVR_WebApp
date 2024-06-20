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
function hsvToRgb(h, s, v) {
    const c = v * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = v - c;

    let r, g, b;
    if (h >= 0 && h < 60) {
        [r, g, b] = [c, x, 0];
    } else if (h >= 60 && h < 120) {
        [r, g, b] = [x, c, 0];
    } else if (h >= 120 && h < 180) {
        [r, g, b] = [0, c, x];
    } else if (h >= 180 && h < 240) {
        [r, g, b] = [0, x, c];
    } else if (h >= 240 && h < 300) {
        [r, g, b] = [x, 0, c];
    } else {
        [r, g, b] = [c, 0, x];
    }

    return [
        Math.round((r + m) * 255),
        Math.round((g + m) * 255),
        Math.round((b + m) * 255)
    ];
}

function rgbToHex(r, g, b) {
    return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1)}`;
}

function random(min, max) {
    return Math.random() * (max - min) + min;
}

function genOptionColorGradient(n) {
    // function to generate a color gradient based on two random picked colors and interpolating Hue for n colors

    const colors = [];
    const firstHue = random(0, 360);
    const secondHue = (firstHue + random(30, 150)) % 360;


    // change these two constants to adjust color generation
    const randS = random(0.5, 1)  // Saturation - pale (0) to vivid (1)
    const randV = random(0.6, 1)  // Intensity Value - dark (0) to light (1)


    const firstColor = hsvToRgb(firstHue, randS, randV);
    const secondColor = hsvToRgb(secondHue, randS, randV);

    if (n === 1) {
        colors.push(rgbToHex(...firstColor));
    } else if (n === 2) {
        colors.push(rgbToHex(...firstColor), rgbToHex(...secondColor));
    } else if (n > 2) {
        for (let i = 0; i < n; i++) {
            const currentHue = firstHue + ((secondHue - firstHue) / (n - 1)) * i;
            const currentColor = hsvToRgb(currentHue, randS, randV);
            colors.push(rgbToHex(...currentColor));
        }
    }

    return colors;
}
function reconnect() {
    location.reload()
}
function removeAllChildNodes(parent) {
    if (parent) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild);
        }
    }

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
