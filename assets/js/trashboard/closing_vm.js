

ClosingVM = function(master) {
    var self = new BaseSectionVM(master);

    self.name = 'closing';

    self.is_completed = ko.computed(function() {
        return true;
    });

    self.available_products = function() {
        return _.filter(window.PRODUCTS_BY_TYPE.Closer, function(product) {
            return product.product_price;
        });
    }
    self.generate_customizers();

    return self;
};
