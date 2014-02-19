

/* Every VM needs this stuff. */

function BaseSectionVM(master) {
    var self = new UpdatableAndSerializable();

    self.master = master;
    self.customizers = ko.observableArray([]);

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

    self.get_css_classes = function() {
        /*
       'complete': vm.is_completed(),
       'incomplete': !vm.is_completed(),
       */
       var classes = ['vm', self.is_completed() ? 'complete' : 'incomplete', self.name];
       return classes.join(' ');

    }


    self.upfront_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            console.log('Upfront subtotal for vm ', self.name, ' adding ', cust.quantity(), ' of ', cust.code, ' at ', cust.price.upfront_price);
            if(cust.quantity() && cust.price.upfront_price) {
                total_balance += cust.price.upfront_price * cust.quantity()
            }
        });
        return total_balance;
    });

    self.monthly_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            if(cust.quantity() && cust.price.monthly_price) {
                total_balance += cust.price.monthly_price * cust.quantity()
            }
        });
        return total_balance;
    });

    self.cb_balance = ko.computed(function() {
        var total_cb = 0;
        _.each(self.customizers(), function(cust) {
            if(cust.chargedback() && cust.quantity() && cust.price.cb_points) {
                total_balance += cust.quantity() * cust.price.cb_points;
            }
        });
        return total_cb;
    })

    // API link
    self.construct_agreement = function(agreement) {
        /* Update the passed in agreement blob with data from the fields
           on this vm. */

    };

    self.update_from_agreement = function(agreement) {
        /* Given an agreement blob, update the fields on this vm.  (This
        should cause the templates to update). */


    };

    self.available_products = function() {
        return [];
    }

    self.generate_customizers = function() {
        _.each(self.available_products(), function(product) {
            if(!product.product_price) {
                console.log("Skipping ", product, "because it has no product_price.");
                return;
            }

            var internal_obs = ko.observable(0);

            var quantity = ko.computed({
                'read': internal_obs,
                'write': function(newval) {

                    // http://stackoverflow.com/questions/175739/is-there-a-built-in-way-in-javascript-to-check-if-a-string-is-a-valid-number

                    if(!/^(\d+|)$/.test(newval)) {
                        // If the entry is not blank or a sequence of digits,
                        // This little magic doodad causes the text box that had stupid
                        // in it to revert to the value in the model:

                        // https://github.com/knockout/knockout/issues/1019#issuecomment-21777977
                        quantity.notifySubscribers(quantity())
                        return;
                    }
                    // Otherwise, cast it to an int and put it in.
                    internal_obs(+newval);
                }
            });

            var one_or_none = ko.computed({
                'read': function() {
                    console.log("reading ", !!quantity());
                    return !!quantity();
                },
                'write': function(yesno) {
                    console.log("Writing ", +yesno);
                    quantity(+yesno);
                }
            });

            var cust = {
                'code': product.code,
                'name': product.name,
                'product': product,
                'price': product.product_price,
                'min_quantity': ko.observable(0),
                'base_quantity': ko.observable(0),
                'quantity': quantity,
                'chargedback': ko.observable(false),
                'one_or_none': one_or_none
            };

            self.customizers.push(cust);
            //self.computed_quantity[product.code].internal_obs = internal_obs;
        });
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




    return self;
}