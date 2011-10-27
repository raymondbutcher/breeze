var $scripts = (function($loader) {
    var registry = {};
    function loadScripts(scriptNames) {
        /*
          Loads a single script or a list of scripts by name.
          Handles all dependencies as configured in the registry.
        */
        var scriptList = scriptNames['push'] ? scriptNames : [scriptNames];
        scriptList.forEach(function(scriptName) {
            var script = registry[scriptName];
            if (script.requires) {
                $loader.ready(script.requires, function() {
                    $loader(script.path, scriptName);
                }, loadScripts);
            } else {
                $loader(script.path, scriptName);
            }
        });
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
        register: registerScripts
    }
})($script);
