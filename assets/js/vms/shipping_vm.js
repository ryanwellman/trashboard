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

    self.select_shipping = function(cline) {
        self.selected(cline);
    }


    self.shipping_css = function(cline) {
        var classes = ['shipping', cline.product.code];
        if(cline === self.selected()) {
             classes.push('selected');
        }
        return classes.join(' ');
    }



    return self;

}
