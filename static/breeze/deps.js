/*
    Dependency manager

    Original loader script taken from https://github.com/ded/script.js

    Updated to support:
        * A registry of dependencies
        * Automatic loading of scripts as needed.
        * Allow extra attributes on the script tags when being loaded.
        * Allow loading CSS.

*/

!function (name, definition) {
  if (typeof define == 'function') define(definition)
  else if (typeof module != 'undefined') module.exports = definition()
  else this[name] = definition()
}('$script', function() {
  var win = this, doc = document
    , head = doc.getElementsByTagName('head')[0]
    , validBase = /^https?:\/\//
    , old = win.$script, list = {}, ids = {}, delay = {}, scriptpath
    , scripts = {}, s = 'string', f = false
    , push = 'push', domContentLoaded = 'DOMContentLoaded', readyState = 'readyState'
    , addEventListener = 'addEventListener', onreadystatechange = 'onreadystatechange'
    , isCSS = /^.+\.css(\?.*)?$/

  function every(ar, fn, i) {
    for (i = 0, j = ar.length; i < j; ++i) if (!fn(ar[i])) return f
    return 1
  }
  function each(ar, fn) {
    every(ar, function(el) {
      return !fn(el)
    })
  }

  if (!doc[readyState] && doc[addEventListener]) {
    doc[addEventListener](domContentLoaded, function fn() {
      doc.removeEventListener(domContentLoaded, fn, f)
      doc[readyState] = 'complete'
    }, f)
    doc[readyState] = 'loading'
  }

  function $script(paths, idOrDone, optDone) {
    paths = paths[push] ? paths : [paths]
    var idOrDoneIsDone = idOrDone && idOrDone.call
      , done = idOrDoneIsDone ? idOrDone : optDone
      , id = idOrDoneIsDone ? paths.join('') : idOrDone
      , queue = paths.length
    function loopFn(item) {
      return item.call ? item() : list[item]
    }
    function callback() {
      if (!--queue) {
        list[id] = 1
        done && done()
        for (var dset in delay) {
          every(dset.split('|'), loopFn) && !each(delay[dset], loopFn) && (delay[dset] = [])
        }
      }
    }
    setTimeout(function () {
      each(paths, function(path) {
        if (scripts[path]) {
          id && (ids[id] = 1)
          return scripts[path] == 2 && callback()
        }
        scripts[path] = 1
        id && (ids[id] = 1)
        create(!validBase.test(path) && scriptpath ? scriptpath + path + '.js' : path, callback)
      })
    }, 0)
    return $script
  }

  function createCSS(path, fn) {
    var el = doc.createElement('link')
      , loaded = f
    el.type = 'text/css'
    el.rel = 'stylesheet'
    el.href = path
    var attrs = $deps.attrs(path)
    for (name in attrs) {
        el.setAttribute(name, attrs[name]);
    }
    head.insertBefore(el, head.firstChild)
    loaded = 1
    scripts[path] = 2
    fn()
  }

  function createScript(path, fn) {
    var el = doc.createElement('script')
      , loaded = f
    el.onload = el.onerror = el[onreadystatechange] = function () {
      if ((el[readyState] && !(/^c|loade/.test(el[readyState]))) || loaded) return;
      el.onload = el[onreadystatechange] = null
      loaded = 1
      scripts[path] = 2
      fn()
    }
    el.async = 1
    el.src = path
    var attrs = $deps.attrs(path)
    for (name in attrs) {
        el.setAttribute(name, attrs[name]);
    }
    head.insertBefore(el, head.firstChild)
  }

  function create(path, fn) {
    if (isCSS.test(path)) {
        createCSS(path, fn);
    } else {
        createScript(path, fn);
    }
  }

  $script.get = create

  $script.order = function (scripts, id, done) {
    (function callback(s) {
      s = scripts.shift()
      if (!scripts.length) $script(s, id, done)
      else $script(s, callback)
    }())
  }

  $script.path = function(p) {
    scriptpath = p
  }
  $script.ready = function(deps, ready, req) {
    deps = deps[push] ? deps : [deps]
    var missing = [];
    !each(deps, function(dep) {
      list[dep] || missing[push](dep);
    }) && every(deps, function(dep) {return list[dep]}) ?
      ready() : !function(key) {
      delay[key] = delay[key] || []
      delay[key][push](ready)
      req && req(missing)
    }(deps.join('|'))
    return $script
  }

  $script.noConflict = function () {
    win.$script = old;
    return this
  }

  return $script
})


var $deps = (function($loader) {
    
    var registry = {};
    
    function getAttrs(path) {
        for (var scriptName in registry) {
            var script = registry[scriptName];
            if (script.path == path) {
                return script.attrs || {};
            }
        }
        return {};
    }
    
    function loadScripts(scriptNames) {
        /*
          Loads a single script or a list of scripts by name.
          Handles all dependencies as configured in the registry.
        */
        var scriptList = scriptNames['push'] ? scriptNames : [scriptNames];
        
        for (var i=0; i<scriptList.length; i++) {
            var scriptName = scriptList[i];
            var script = registry[scriptName];
            if (script.requires) {
                $loader.ready(script.requires, function() {
                    $loader(script.path, scriptName);
                }, loadScripts);
            } else {
                $loader(script.path, scriptName);
            }
        }
    }
    
    function ready(requiredScripts, callbackFunction) {
        /*
          Runs a function when the required scripts have been
          loaded. Automatically loads the required scripts and
          handles all dependencies as configured in the registry.
        */
        $loader.ready(requiredScripts, callbackFunction, loadScripts);
    }
    
    function registerScripts(info) {
        /* Registers scripts to be used for loading and dependencies. */
        for (var scriptName in info) {
            registry[scriptName] = info[scriptName]
        }
    }
    
    return {
        load: loadScripts,
        ready: ready,
        register: registerScripts,
        attrs: getAttrs
    }
})($script);
