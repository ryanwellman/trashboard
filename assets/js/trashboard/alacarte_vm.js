
AlaCarteLineVM = function(blob) {

    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "quantity": ko.observable(blob.quantity || 0),
        "part": ko.observable(null),
    };

    _.each(self.fields, function(field, name) {
        self[name] = field;
    });

    self.code = ko.computed({
        'read': function() {
            if(!self.part()) return null;
            return self.part().code;
        },
        'write': function(newcode) {
            var part = window.PRODUCTS[newcode];
            self.part(part || null);
        }
    });

    if(self.code()) {
        self.part(window.PRODUCTS[self.code()])
    }

    self.upfront_subtotal = ko.computed(function() {
        // ko.computeds only update when an observable they referenced on their first run (undocumented!)
        // changes; we must use this arcane, twisted way of returning zero
        self.quantity();

        if(self.part()) {
            return self.part().product_price.upfront_price * self.quantity();
        } else {
            return 0;
        }
    });
    self.monthly_subtotal = ko.computed(function() {
        // ko.computeds only update when an observable they referenced on their first run (undocumented!)
        // changes; we must use this arcane, twisted way of returning zero
        self.quantity();

        if(self.part()) {
            return self.part().product_price.monthly_price * self.quantity();
        } else {
            return 0;
        }
    });

    return self;
};

ALaCarteVM = function(master) {
    var self = new BaseSectionVM(master);
    self.name = 'alacarte';


    self.fields = {

    };

    _.each(self.fields, function(field, name) {
        self[name] = field;
    });


    self.available_products = function(agreement) {
        return _.filter(window.PRODUCTS_BY_TYPE.Part, function(product) {
            return product.product_price;
        });
    };

    self.generate_customizers();

    self.is_completed = ko.computed(function() {
        return !self.customizing();
    });

    // alacarte vm is kind of special, it needs to be able to fill its internal array from the blob
    self.construct_agreement = function(agreement) {


    };

    self.update_from_agreement = function(agreement) {

    };

    /*
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
    */


    return self;
};
