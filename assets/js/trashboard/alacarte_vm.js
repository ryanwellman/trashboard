
AlaCarteLineVM = function(blob) {

    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "selected_part": PartVM,
        "quantity": ko.observable,
    };

    // ...since the knockout bindings of each drop-down are the actual PartVMs we created above
    // this vm is also special in that it needs to be able to fill itself from the blob but not
    // with just any old unregulated PartVM; they must be the ones that knockout knows about
    self['quantity'] = fields['quantity'](blob['quantity']);
    self['selected_part'] = window.DPARTS[blob['selected_part']['code']];

    self.total_price = ko.computed(function() {
        // ko.computeds only update when an observable they referenced on their first run (undocumented!)
        // changes; we must use this arcane, twisted way of returning zero
        self.quantity();
        if(self.selected_part) {
            return (self.selected_part.code() && self.selected_part.price()) ? self.quantity() * self.selected_part.price() : 0.00;
        } else {
            return self.quantity() * 0; // drop-down is empty
        }
    });

    self.returnFields = function() {
        return fields;
    };

    self._serialize = function() {
        return ko.toJSON({ 'code': self.selected_part.code(), 'quantity': self.quantity() });
    };

    return self;
};

ALaCarteVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "purchase_lines": ko.observableArray, // contains non-observable AlaCarteLineVMs
        "done": ko.observable,
    };

    // alacarte vm is kind of special, it needs to be able to fill its internal array from the blob
    self['done'] = fields['done'](blob['done']);
    self['purchase_lines'] = fields['purchase_lines']();
    _.each(blob['purchase_lines'], function(v, k) {
        self.purchase_lines().push(new AlaCarteLineVM(v));
        self.purchase_lines.valueHasMutated();
    });

    self.returnFields = function() {
        return fields;
    };

    self.dirtyRefresh = function () {
        // non-observable contents of observable arrays need this to work when valueHasMutated won't
        // http://stackoverflow.com/questions/13231738/refresh-observablearray-when-items-are-not-observables
        var data = self.purchase_lines();
        self.purchase_lines([]);
        self.purchase_lines(data);
    };

    self.addLine = function() {
        self.purchase_lines().push(new AlaCarteLineVM({'selected_part': {}, 'quantity': 0}));
        self.purchase_lines.valueHasMutated();
    };

    self.removeLine = function(line) { alert('removing!'); self.purchase_lines.remove(line) };

    self.save = function() {
        alert('{'+$.map(self.purchase_lines(), function(val) { return val._serialize(); }) + '}');
    }

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};
