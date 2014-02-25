
// Package is similar to closers in that we just render the customization lines as boxes.
// The biggest difference is that it ALSO has a sub vm inside of it.
PackageVM = function(master) {
    var self = new BaseSectionVM(master);
    self.name = 'package';
    var fields = {

    };



    // copy them out of fields onto this itself.
    _.each(fields, function(v, k) {
         self[k] = v;
    });


    self.available_products = ko.computed(function() {
        return _.filter(window.catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.product_type === 'Package';
        });
    });



    self.customize_vm = CustomizationVM(master, self);

    self.is_completed = ko.computed(function() {
        return !!self.selected() && self.customize_vm.is_completed();
    });

    self.select_package = function(cust) {
        self.selected(cust);
    };

    self.onSelectedChange = function() {
        self.customize_vm.reset_customizations();
    };

    var SUPER_update_cart_lines = _.bind(self.update_cart_lines, self);
    self.update_cart_lines = function() {
       SUPER_update_cart_lines();
       self.customize_vm.update_cart_lines();
    }

    // This is a little weird.  I'm not sure what having one computed calling another is going to
    // do exactly, with this "super" computed call.  I THINK it'll work as intended.  The super
    // computed will get events, and its update will trigger THIS one to update.
    var SUPER_cb_balance = _.bind(self.cb_balance, self);
    self.cb_balance = ko.computed(function() {
        var bal = SUPER_cb_balance();
        bal += self.customize_vm.cb_balance();
        return bal;
    });

    self.package_css = function(cust) {
        var classes = ['package', cust.product.code];
        if(cust === self.selected()) {
             classes.push('selected');
        }
        return classes.join(' ');
    }

    var SUPER_construct_agreement = _.bind(self.construct_agreement, self);
    self.construct_agreement = function(agreement) {
        SUPER_construct_agreement(agreement);

        // Let customization vm do some stuff.
        self.customize_vm.construct_agreement(agreement);
    };

    return self;
};



CustomizationVM = function(master, package_vm) {
    var self = new BaseSectionVM(master);
    self.name = 'customization';
    self.package_vm = package_vm;

    var fields = {

    };

    // copy them out of fields onto this itself.
    _.each(fields, function(v, k) {
         self[k] = v;
    });


    self.is_completed = ko.computed(function() {
        return !self.customizing();
    });

    self.available_products = ko.computed(function() {
        return _.filter(window.catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.product_type === 'Part';
        });
    });

    self.reset_customizations = function() {
        var sel = self.package_vm.selected();
        var contents = {};
        if(sel) {
            var package = sel.product;
            contents = _.indexBy(package.contents, function(pc) {
                return pc.code;
            });
        }

        _.each(self.customizers(), function(cust) {
            var pc = contents[cust.code];
            if(!pc) {
                cust.min_quantity(0);
                cust.base_quantity(0);
                cust.quantity(0);
            } else {
                console.log('updating a cust');
                cust.min_quantity(pc.min_quantity);
                cust.base_quantity(pc.quantity);
                cust.quantity(cust.base_quantity());
            }

        });
    };

    // Customizations have no price total.  It's always included in the package.
    self.monthly_subtotal = ko.computed(function() {
        return 0;
    });
    self.upfront_subtotal = ko.computed(function() {
        return 0;
    });

    // However, every line has a chargeback cost based on the delta of quantities.
    self.cb_balance = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            total_balance += cust.customize_cb();
        });
        return total_balance;
    });

    self.construct_agreement = function(agreement) {
        console.log("About to call self.customizations on ", self);
        _.each(self.customizers(), function(cust) {
            // Skip if they are the same.
            if(cust.quantity() === cust.base_quantity()) {
                return;
            }
            var delta = cust.quantity() - cust.base_quantity();
            // store the trade delta as the invoice line quantity
            agreement.invoice_lines.push({
                'product': cust.code,
                'quantity': delta,
                'traded': true
            });

        });
    };

    self.update_from_agreement = function(agreement) {
        var trade_lines = _.filter(agreement.invoice_lines, function(iline) {
            return iline.traded;
        });

        var trade_lines_by_code = _.index(trade_lines, function(tline) {
            return tline.product;
        });

        _.each(self.customizations(), function(cust) {
            var tline = trade_lines_by_code[cust.code];
            if(tline) {
                // Using the trade delta, assign the current total quantity.
                cust.quantity(cust.base_quantity() + tline.quantity);
            }
        });
    };


    return self;
};
