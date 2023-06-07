class VariableListener {
  constructor(obj) {
    this.obj = obj;
    this.keys = Object.keys(obj);
    this.init();
  }
  toString() {
    return this.constructInternalObject();
  }
  init() {
    for (var i = 0; i < this.keys.length; i++) {
      var key = this.keys[i];
      var value = this.obj[key];
      if (value == undefined) {
        continue;
      }
      this.addListener(key, value);
    }
  }
  constructInternalObject() {
    var internalObjects = {};
    for (var i = 0; i < this.keys.length; i++) {
      var key = this.keys[i];
      var value = this.obj[key];

      if (this[key + "Internal"] == undefined) {
        continue;
      }
      if (isJsonObject(value)) {
        internalObjects[key.replace("Internal", "")] =
          value.constructInternalObject();
      }
      internalObjects[key] = this[key + "Internal"];
    }
    return internalObjects;
  }
  addListener(key, value) {
    if (!this.keys.includes(key)) {
      this.keys.push(key);
    }
    if (isJsonObject(value)) {
      value = new VariableListener(value);
    }
    this[key + "Internal"] = value;
    this[key + "Listener"] = function (val) {
      // console.log("updated:\n");
      // console.log(val);
    };
    Object.defineProperty(this, key, {
      get() {
        return this[key + "Internal"];
      },
      set(val) {
        if (isJsonObject(val)) {
          val = new VariableListener(val);
        }
        this[key + "Internal"] = val;
        this[key + "Listener"](val);
      },
      configurable: true,
    });

    this[key + "RegisterListener"] = function (new_function) {
      this[key + "Listener"] = (function (old_function, new_function) {
        return function extendedFunction(val) {
          old_function(val);
          new_function(val);
        };
      })(this[key + "Listener"], new_function);
    };
  }
  update(obj) {
    var keys = Object.keys(obj);
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      // check if key is present in the object
      if (!this.keys.includes(key)) {
        this.addListener(key, obj[key]);
        continue;
      }
      if (obj[key] instanceof VariableListener) {
        this[key].update(obj[key]);
        continue;
      }
      this[key] = obj[key];
    }
    var keys = Object.keys(obj);
    for (var i = 0; i < this.keys.length; i++) {
      var key = this.keys[i];
      if (!keys.includes(key)) {
        this[key] = "";
        keys.push(key);
      }
    }
  }
}

function variableListener(obj) {
  var keys = Object.keys(obj);
  newListnerObject = {};
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    var value = obj[key];
    if (value == undefined) {
      continue;
    }
    newListnerObject = addListener(newListnerObject, key, obj[key]);
  }
  newListnerObject.getInternals = function () {
    return constructInternalObject(this);
  };
  return newListnerObject;
}

function isJsonObject(obj) {
  if (typeof obj !== "object" || obj === null || Array.isArray(obj)) {
    return false;
  }
  try {
    JSON.stringify(obj);
    return true;
  } catch (e) {
    return false;
  }
}
