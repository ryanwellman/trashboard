
ALaCarteVM = function(master) {
    var self = new BaseSectionVM(master);
    self.name = 'alacarte';


    self.fields = {

    };

    _.each(self.fields, function(field, name) {
        self[name] = field;
    });

    self.available_products = ko.computed(function() {
        return _.filter(catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.price().available && prod.product_type === 'Part';
        });
    });

    self.is_completed = ko.computed(function() {
        return !self.customizing();
    });



    return self;
};
