
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
            dataType: "json",
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
        payload = JSON.stringify(agreement)
        var retval = '';

        var result = $.ajax({
            type: "POST",
            dataType: "json",
            url: '/json/' + window.agreement_id,
            async: false, // testing with and without this
            data: payload,
        });

        result.fail(function(xhr, status, error) {
            console.log('failed! (' + error + ') ' + status);
            console.log(xhr.responseText);
        });

        result.done(function(data) {
            // obtain that agreement id from the json response
            console.log(data);
            obj.id = data.id;  // scope spam
            window.agreement_id = data.id;
            retval = data.id;
            console.log("saved json" + (window.agreement_id ? " to agreement " + window.agreement_id :  '') + "\n" + ko.toJSON(self));
        });

        // return the agreement id that was saved
        return retval;
    };
};
