

/* Every VM needs this stuff. */

function BaseSectionVM(master) {
    var self = new UpdatableAndSerializable();

    self.master = master;

    // Only used for sections that lock-in edits for convenience. (package, alacarte)
    self.customizing = ko.observable(false);

    /* These functions have default implementations (sometimes), but you can't super.
       These are just stubs that explain what the functions need to test/do. */

    //Template rendering.
    self.nav_template_name = function() {
        return 'default_nav_template';
    }

    self.template_name = function() {
        return self.name+'_vm';
    }

    self.is_completed = ko.computed(function() {
        return false;
    });

    // Display parameters

    self.display_label = function() {
        if(self.name) {
            return (self.name.substr(0,1).toUpperCase() + self.name.substr(1)).replace('_', ' ');
        }
        return 'Unknown section';
    }

    self.cart_heading_label = function() {
        return self.display_label();
    }

    self.get_css_classes = function() {
        /*
       'complete': vm.is_completed(),
       'incomplete': !vm.is_completed(),
       */
       var classes = ['vm',
                      self.is_completed() ? 'complete' : 'incomplete',
                      self.name];
       return classes.join(' ');

    }


    // API link
    self.construct_agreement = function(agreement) {
        /* Update the passed in agreement blob with data from the fields
           on this vm. */

        var custs = self.nonzero_customizations();
        _.each(custs, function(cline) {
            var il = {
                'code': cline.code,
                'quantity': cline.quantity()
            };
            agreement.invoice_lines.push(il);
        });
    };

    self.update_from_agreement = function(agreement) {
        /* Given an agreement blob, update the fields on this vm.  (This
        should cause the templates to update). */
        self.update_cart_from_agreement(agreement);

    };
    self.update_cart_from_agreement = function(agreement) {
        var top_levels = _.filter(agreement.invoice_lines, function(iline) {
            return !iline.traded && !iline.parent_id && !iline.mandatory;
        });

        console.log("Update cart from agreement in ", self.name, " using ", top_levels);
        var lines_by_code = _.indexBy(top_levels, function(iline) {
            return iline.product;
        });

        _.each(self.cart_lines(), function(cline) {
            var il = lines_by_code[cline.code];
            cline.quantity(il ? il.quantity : 0);
        });
    };

    self.available_products = function() {
        return [];
    }



    //trigger with cart_trigger.valueHasMutated();
    self.cart_trigger = ko.observable().extend({'notify': 'always'});

    self.cart_lines = ko.computed(function() {
        self.cart_trigger();
        var codes = _.map(self.available_products(), function(product) {
            return product.code;
        });
        return _.filter(master.cart.cart_lines(), function(cline) {
            return codes.indexOf(cline.code) !== -1;
            // same as
            // return ~codes.indexOf(cline.code);
        });
    });



    self.upfront_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.cart_lines(), function(cline) {
            //console.log('Upfront subtotal for vm ', self.name, ' adding ', cline.quantity(), ' of ', cline.code, ' at ', cline.price().upfront_price);
            if(cline.quantity() && cline.price().upfront_price) {
                total_balance += cline.price().upfront_price * cline.quantity()
            }
        });
        return total_balance;
    });

    self.monthly_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.cart_lines(), function(cline) {
            if(cline.quantity() && cline.price().monthly_price) {
                total_balance += cline.price().monthly_price * cline.quantity()
            }
        });
        return total_balance;
    });

    self.cb_balance = ko.computed(function() {
        var total_cb = 0;
        _.each(self.cart_lines(), function(cline) {
            if(cline.chargedback() && cline.quantity() && cline.price().cb_points) {
                total_balance += cline.quantity() * cline.price().cb_points;
            }
        });
        return total_cb;
    })



    self.nonzero_customizations = ko.computed(function() {
        return _.filter(self.cart_lines(), function(cline) {
            return cline.quantity();
        });
    });

    // This is neat.  Selected is automatically the first customizer with a positive quantity.
    self.selected = ko.computed({
        'read': function() {
            console.log("calculating selected.");
            var sel = _.find(self.cart_lines(), function(cline) {
                return cline.quantity() > 0;
            });
            return sel;
        },
        'write': function(sel) {
            console.log("Setting selected to ", sel ? sel.product.code : sel);
            _.each(self.cart_lines(), function(cline) {
                cline.quantity( cline === sel ? 1 : 0 );
            });

            console.log("Calling onSelectedChange on ", self.name);
            self.onSelectedChange();

            self.selected.notifySubscribers(self.selected());
        }
    });


    self.onSelectedChange = function() {

    };

    self.start_customizing = function(data, eargs) {
        if(eargs && eargs.preventDefault) {
            eargs.preventDefault();
        }
        self.customizing(true);
    };
    self.finish_customizing = function(data, eargs) {
        if(eargs && eargs.preventDefault) {
            eargs.preventDefault();
        }
        self.customizing(false);
    };

    self.select_row = function(cline, eargs) {
        console.log("You clicked a row.");

        if(eargs && eargs.preventDefault) {
            eargs.preventDefault();
            eargs.stopPropagation();
        }
        if(self.selected() !== cline) {
            self.selected(cline);
        }
    };


    return self;
}