

// contains invoice lines
ReviewVM = function(master) {
    // capture a new copy of UAS and make this thing
    var self = new BaseSectionVM(master);
    self.name = 'review';

    // field types
    var fields = {
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.available_products = function() {
        return [];
    };

    self.is_completed = function() {
        return !master.dirty();
    };

/*
    self.cart_lines = ko.computed(function() {
        self.cart_trigger();

        return [];

        return _.union(master.cart.cart_lines(), master.customization_cart.cart_lines());

    });

    self.top_lines = ko.computed(function() {
        self.cart_trigger();
        return _.filter(master.cart.cart_lines(), function(cline) {
            return cline.quantity();
        });
    });

    self.trade_lines = ko.computed(function() {
        self.cart_trigger();
        return _.filter(master.customization_cart.cart_lines(), function(tline) {
            return tline.quantity();
        });
    });

*/

    self.invoice_lines = ko.observableArray([]);

    self.update_from_agreement = function(agreement) {
        var by_id = _.indexBy(agreement.invoice_lines, function(iline) {
            return iline.id;
        });


        var last_by_type = {};

        _.each(agreement.invoice_lines, function(iline) {
            iline.parent = by_id[iline.parent_id] || null;
            iline.product = catalog.PRODUCTS_BY_CODE[iline.code];
            if(!iline.product) {
                console.log("Somethign is wrong, ", iline.code, iline.product);
            }

            last_by_type[iline.product.product_type] = iline;
        });

        var result_set = _.compact([
            last_by_type.Package,
            last_by_type.Monitoring,
            last_by_type.Shipping,
        ]);

        var tops = _.filter(agreement.invoice_lines, function(iline) {
            return !iline.parent;
        });

        result_set = _.union(result_set, tops);

        var children = _.filter(agreement.invoice_lines, function(iline) {
            return iline.parent;
        });

        _.each(children, function(iline) {
            result_set.splice(result_set.indexOf(iline) + 1, 0, iline);
        });
        _.each(result_set, function(iline) {
            if(!iline.parent) {
                iline.depth = 0;
            } else {
                iline.depth = iline.parent.depth + 1;
            }

            iline.upfront_each_fmted = formatCurrency(iline.upfront_strike || iline.upfront_each);
            iline.monthly_each_fmted = formatCurrency(iline.monthly_strike || iline.monthly_each, 1, 'monthly');

            iline.upfront_total_fmted = formatCurrency(iline.upfront_strike || iline.upfront_total, iline.quantity);
            iline.monthly_total_fmted = formatCurrency(iline.monthly_strike || iline.monthly_total, iline.quantity, 'monthly');


        });


        self.invoice_lines(result_set);


    };

    self.top_invoice_lines = ko.computed(function() {
        return _.filter(self.invoice_lines(), function(iline) {
            return !iline.parent;
        });
    });

    self.construct_agreement = function(agreement) {

    };



    return self;
};

