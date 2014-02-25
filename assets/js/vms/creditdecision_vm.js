// contains this agreement's credit response
CreditDecisionVM = function(blob) {
    // capture a new copy of UAS and make this thing
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't
    blob = blob || {};

    // field types
    var fields = {
        'decision': ko.observable,
        'files': ko.observableArray,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // XXX: additional processing unknown?
};
