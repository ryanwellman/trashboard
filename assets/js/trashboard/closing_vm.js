

ClosingVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_codes': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // ko needs the things in selected_codes to be things from window vars
    codes = []
    _.each(self.selected_codes(), function(v, k) {
        codes.push(window.closer_index[v.code]);
    });
    self.selected_codes(codes);

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};
