class VariableListener {
  constructor(obj) {
    this.obj = obj;
    this.keys = Object.keys(obj);
    this.init();
  }
  toString() {
    return "VariableListener object";
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
    this.getInternals = function () {
      return this.constructInternalObject();
    };
  }
  constructInternalObject() {
    var internalObjects = {};
    for (var i = 0; i < this.keys.length; i++) {
      var key = this.keys[i];
      var value = this.obj[key];

      if (value == undefined) {
        continue;
      }
      if (isJsonObject(value)) {
        value.constructInternalObject();
      }
      if (key.endsWith("Internal")) {
        internalObjects[key.replace("Internal", "")] = value;
      }
    }
    return internalObjects;
  }
  addListener(key, value) {
    if (isJsonObject(value)) {
      value = new VariableListener(value);
    }
    this[key + "Internal"] = value;
    this[key + "Listener"] = function (val) {
      // console.log("updated:\n" + val);
    };
    Object.defineProperty(this, key, {
      set: function (val) {
        if (isJsonObject(val)) {
          val = new VariableListener(val);
        }
        this[key + "Internal"] = val;
        this[key + "Listener"](val);
      },
      get: function () {
        return this[key + "Internal"];
      },
    });

    this[key + "RegisterListener"] = function (new_function) {
      this[key + "Listener"] = (function (old_function, new_function) {
        function extendedFunction(val) {
          old_function(val);
          new_function(val);
        }
        return extendedFunction;
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
        this.keys.push(key);
      } else {
        if (isJsonObject(obj[key])) {
          this[key].update(obj[key]);
        } else {
          this[key] = obj[key];
        }
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
