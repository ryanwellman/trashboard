function ShippingVM(master) {
    var self = new BaseSectionVM(master);
    self.name = 'shipping';

    var fields = {

    };

    _.each(fields, function(v, k) {
        self[k] = v;
    });




    self.available_products = ko.computed(function() {
        return _.filter(window.catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.product_type === 'Shipping';
        });
    });

    self.is_completed = ko.computed(function() {
        return !!self.selected();
    });

    self.select_shipping = function(cust) {
        self.selected(cust);
    }


    self.shipping_css = function(cust) {
        var classes = ['shipping', cust.product.code];
        if(cust === self.selected()) {
             classes.push('selected');
        }
        return classes.join(' ');
    }



    return self;

}
