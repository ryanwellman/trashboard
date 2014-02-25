
ComboVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_codes': ko.observableArray,
        'contents': ko.observableArray,
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
        codes.push(window.premium_index[v.code]);
    });
    self.selected_codes(codes);

    self.select_item = function() {
        self.contents.removeAll();
        for(var i = 0; i < self.selected_codes().length; i++) {
            console.log(self.selected_codes()[i].contents);
            for(var j = 0; j < self.selected_codes()[i].contents.length; j++) {
                var ret = {
                    'code': self.selected_codes()[i].contents[j].code,
                    'quantity': self.selected_codes()[i].contents[j].quantity,
                };

                self.contents.push(ret);
            }
        }

        // required for ko to allow checkbox to click
        return true;
    };

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};
