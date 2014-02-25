

ClosingVM = function(master) {
    var self = new BaseSectionVM(master);

    self.name = 'closing';

    self.is_completed = ko.computed(function() {
        return true;
    });

    self.available_products = ko.computed(function() {
        return _.filter(catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.product_type === 'Closer';
        });
    });

    return self;
};
