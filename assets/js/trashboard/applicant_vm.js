
// refer to the comments in MasterVM to understand the next two objects
ApplicantVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'fname': ko.observable,
        'lname': ko.observable,
        'initial': ko.observable,
        'phone': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.complete = function() {
        return self._test([self.fname() && self.lname()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
    };

    return self;
};