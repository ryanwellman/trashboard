
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
            return prod.price() && prod.price().available && prod.product_type === 'Package';
        });
    });



    self.customize_vm = CustomizationVM(master, self);

    self.is_completed = ko.computed(function() {
        return !!self.selected() && self.customize_vm.is_completed();
    });

    self.select_package = function(cline) {
        self.selected(cline);
    };

    self.onSelectedChange = function() {
        self.customize_vm.reset_customizations();
    };

/*
    var SUPER_update_cart_lines = _.bind(self.update_cart_lines, self);
    self.update_cart_lines = function() {
       SUPER_update_cart_lines();
       self.customize_vm.update_cart_lines();
    }
*/
    // This is a little weird.  I'm not sure what having one computed calling another is going to
    // do exactly, with this "super" computed call.  I THINK it'll work as intended.  The super
    // computed will get events, and its update will trigger THIS one to update.
    var SUPER_cb_balance = _.bind(self.cb_balance, self);
    self.cb_balance = ko.computed(function() {
        var bal = SUPER_cb_balance();
        bal += self.customize_vm.cb_balance();
        return bal;
    });

    self.package_css = function(cline) {
        var classes = ['package', cline.product.code];
        if(cline === self.selected()) {
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

    var SUPER_update_from_agreement = _.bind(self.update_from_agreement, self);
    self.update_from_agreement = function(agreement) {
        SUPER_update_from_agreement(agreement);

        self.customize_vm.update_from_agreement(agreement);
    }

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
            return prod.product_type === 'Part';
        });
    });

    self.cart_lines = ko.computed(function() {
        package_vm.cart_trigger();
        return _.filter(master.customization_cart.cart_lines(), function(cline) {
            return self.available_products().indexOf(cline.product) != -1;
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

        _.each(self.cart_lines(), function(cline) {
            var pc = contents[cline.code];
            if(!pc) {
                cline.min_quantity(0);
                cline.base_quantity(0);
                cline.quantity(0);
            } else {
                console.log('updating a cline');
                cline.min_quantity(pc.min_quantity);
                cline.base_quantity(pc.quantity);
                cline.quantity(cline.base_quantity());
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
        _.each(self.cart_lines(), function(cline) {
            total_balance += cline.customize_cb();
        });
        return total_balance;
    });

    self.construct_agreement = function(agreement) {
        //console.log("About to call self.customizations on ", self);
        _.each(self.cart_lines(), function(cline) {
            // Skip if they are the same.
            if(cline.quantity() === cline.base_quantity()) {
                return;
            }
            var delta = cline.quantity() - cline.base_quantity();
            // store the trade delta as the invoice line quantity
            agreement.invoice_lines.push({
                'code': cline.code,
                'quantity': delta,
                'line_type': 'TRADE'
            });

        });
    };

    self.update_from_agreement = function(agreement) {

        var trade_lines = _.filter(agreement.invoice_lines, function(iline) {
            return iline.line_type.toUpperCase() == 'TRADE';
        });

        var trade_lines_by_code = _.indexBy(trade_lines, function(tline) {
            return tline.product;
        });

        self.reset_customizations();

        //console.log("In customize_vm's update_from_agreement, tl=", trade_lines, "tlbc=", trade_lines_by_code);
        _.each(self.cart_lines(), function(cline) {
            var tline = trade_lines_by_code[cline.code];
            //console.log("I am searching.  ", cline, tline);
            if(tline) {
                // Using the trade delta, assign the current total quantity.
                cline.quantity(cline.base_quantity() + tline.quantity);
            } else {
                cline.quantity(cline.base_quantity());
            }
        });
    };


    return self;
};
