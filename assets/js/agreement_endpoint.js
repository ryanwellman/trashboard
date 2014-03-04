
AgreementEndpoint = function() {
    // this thing handles loading and saving json-like things to the
    // restful interface

    // capture this into AgreementEndpoint's closure
    var self = this;

    // this fn obtains a json blob from the restful(?) interface
    self._load = function() {
        // obtain a payload
        payload = {};

        // obtain blob from ajax
        var result = $.ajax({
            dataType: "text",
            dataFilter: function(data, type) {
                var loaded = loads(data);
                console.log("Magic loads", loaded);
                return loaded;
            },
            url: '/json/' + window.agreement_id,
            async: false, // asynchronous load means empty blob
        });

        // log failure
        result.fail(function(xhr, status, error) {
            console.log('failed! (' + error + ') ' + status);
            console.log(xhr.responseText);
        });

        // log success
        result.done(function(data) {
            payload = data;
            console.log("loaded json" + (window.agreement_id ? " from agreement " + window.agreement_id : ''));
            console.log(ko.toJSON(data))
        });

        return payload;
    };

    // this fn allegedly saves the contents of obj
    // XXX: needs to be better
    self._save = function(agreement) {
        // obtain a payload and declare a return value outside the promise
        payload = { 'agreement_update_blob': dumps(agreement) };

        var retval;

        var result = $.ajax({
            type: "POST",
            dataType: "text",
            dataFilter: function(data, type) {
                console.log("Got data: ", data);
                var loaded = loads(data);
                console.log("And was able to loads it:", loaded);
                return loaded;

            },
            url: '/json/' + window.agreement_id,
            async: false, // testing with and without this
            data: payload,
            error: function(xhr, status, error) {
                console.log('failed! (' + error + ') ' + status);
                console.log(xhr.responseText);
            },
            success: function(data) {
                // obtain that agreement id from the json response
                /* data will have agreement and errors */
                retval = data;
            }
        });

        // return the agreement id that was saved
        return retval;
    };
};
