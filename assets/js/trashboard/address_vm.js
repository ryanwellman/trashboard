
AddressVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'address': ko.observable,
        'city': ko.observable,
        'state': ko.observable,
        'country': ko.observable,
        'zip': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.complete = function() {
        // we can figure out what country you're in from the state
        return self._test([self.address(), self.city(), self.state(), self.zip()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
    };

    return self;
};