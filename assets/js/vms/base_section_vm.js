

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
       var classes = ['vm',
                      self.is_completed() ? 'complete' : 'incomplete',
                      self.name];
       return classes.join(' ');

    }


    self.upfront_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            //console.log('Upfront subtotal for vm ', self.name, ' adding ', cust.quantity(), ' of ', cust.code, ' at ', cust.price().upfront_price);
            if(cust.quantity() && cust.price().upfront_price) {
                total_balance += cust.price().upfront_price * cust.quantity()
            }
        });
        return total_balance;
    });

    self.monthly_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            if(cust.quantity() && cust.price().monthly_price) {
                total_balance += cust.price().monthly_price * cust.quantity()
            }
        });
        return total_balance;
    });

    self.cb_balance = ko.computed(function() {
        var total_cb = 0;
        _.each(self.customizers(), function(cust) {
            if(cust.chargedback() && cust.quantity() && cust.price().cb_points) {
                total_balance += cust.quantity() * cust.price().cb_points;
            }
        });
        return total_cb;
    })

    // API link
    self.construct_agreement = function(agreement) {
        /* Update the passed in agreement blob with data from the fields
           on this vm. */

        var custs = self.nonzero_customizations();
        _.each(custs, function(cust) {
            var il = {
                'code': cust.code,
                'quantity': cust.quantity()
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
            return !iline.traded && !iline.parent && !iline.mandatory;
        });

        console.log("Update cart from agreement in ", self.name, " using ", top_levels);
        var lines_by_code = _.indexBy(top_levels, function(iline) {
            return iline.product;
        });

        _.each(self.customizers(), function(cust) {
            var il = lines_by_code[cust.code];
            cust.quantity(il ? il.quantity : 0);
        });
    };

    self.nonzero_customizations = ko.computed(function() {
        return _.filter(self.customizers(), function(cust) {
            return cust.quantity();
        });
    });

    self.available_products = function() {
        return [];
    }

    // This is neat.  Selected is automatically the first customizer with a positive quantity.
    self.selected = ko.computed({
        'read': function() {
            console.log("calculating selected.");
            var sel = _.find(self.customizers(), function(cust) {
                return cust.quantity() > 0;
            });
            return sel;
        },
        'write': function(sel) {
            console.log("Setting selected to ", sel ? sel.product.code : sel);
            _.each(self.customizers(), function(cust) {
                cust.quantity( cust === sel ? 1 : 0 );
            });

            console.log("Calling onSelectedChange on ", self.name);
            self.onSelectedChange();

            self.selected.notifySubscribers(self.selected());
        }
    });

    self.onSelectedChange = function() {

    };


    self.update_cart_lines = function() {
        _.each(self.customizers(), function(cust) {
            cust.should_keep = false;
        });
        var existing = _.indexBy(self.customizers(), function(cust) {
            return cust.code;
        });


        _.each(self.available_products(), function(product) {
            if(!product.price()) {
                console.log("Skipping ", product, "because it has no product_price.");
                return;
            }
            var e = existing[product.code];
            if(e) {
                e.name=product.name;
                e.product = product;
                e.price(product.price());
                e.should_keep = true;
                return; //Having updated the prices we're done with this.

            }

            // Make a new cust line.
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
                        quantity.notifySubscribers(quantity());
                        return;
                    }
                    // Otherwise, cast it to an int and put it in.
                    internal_obs(+newval);
                }
            });

            // Reads/writes quantity as a boolean (true=1, false=0)
            var one_or_none = ko.computed({
                'read': function() {
                    //console.log("reading ", !!quantity());
                    return !!quantity();
                },
                'write': function(yesno) {
                    //console.log("Writing ", +yesno);
                    quantity(yesno ? 1 : 0);
                }
            });

            var cust = {
                'code': product.code,
                'name': product.name,
                'product': product,
                'price': ko.observable(product.price()),
                'min_quantity': ko.observable(0),
                'base_quantity': ko.observable(0),
                'quantity': quantity,
                'chargedback': ko.observable(false),
                'one_or_none': one_or_none,
                'should_keep': true,
            };

            cust.customize_quantity = ko.computed({
                'read': quantity,
                'write': function(newval) {
                    var reject = false;
                    if(!/^(\d+|)$/.test(newval)) {
                        reject = true;
                    } else if(+newval < cust.min_quantity()) {
                        reject = true;
                    } else {
                        quantity(newval);
                        return;
                    }

                    // XXX: This guy is pretty weird!
                    quantity.notifySubscribers(quantity());
                    customize_quantity.notifySubscribers(customize_quantity());
                }
            });

            cust.delta_fmted = ko.computed(function() {
                if(cust.quantity() == cust.base_quantity()) {
                    return '';
                } else if (cust.quantity() > cust.base_quantity()) {
                    return '+' + (cust.quantity() - cust.base_quantity());
                } else {
                    return cust.quantity() - cust.base_quantity();
                }
            });


            cust.upfront_each_fmted = ko.computed(function() {
                if(!cust.price() || !cust.price().upfront_price)
                    return '';
                return formatCurrency(cust.price().upfront_price);
            });
            cust.upfront_line_fmted = ko.computed(function() {
               if(!cust.quantity() || !cust.price() || !cust.price().upfront_price)
                   return '';
               return formatCurrency(cust.price().upfront_price * cust.quantity());
            });
            cust.monthly_each_fmted = ko.computed(function() {
                if(!cust.price() || !cust.price().monthly_price)
                    return '';
                return formatCurrency(cust.price().monthly_price) + '/mo';
            });
            cust.monthly_line_fmted = ko.computed(function() {
               if(!cust.quantity() || !cust.price() || !cust.price().monthly_price)
                   return '';
               return formatCurrency(cust.price().monthly_price * cust.quantity()) + '/mo';
            });


            cust.customize_cb = ko.computed(function() {
                return (cust.base_quantity() - cust.quantity()) * cust.price().cb_points;
            });

            cust.is_selected = ko.computed({
                'read': function() {

                    var i_s = self.selected() === cust;
                    console.log("Determining is_selected for ", cust.code, i_s);
                    return i_s
                },
                write: function(checked) {
                    if(checked) {
                        console.log("Selecting package.");
                        self.selected(cust);
                    } else if(!checked && self.selected() === cust) {
                        console.log("Deselecting package.");
                        cust.quantity(0);
                        self.selected(null);


                    }
                    _.defer(function () {
                        // I have no idea why this is necessary.  No amount of
                        // stopping propagation would keep the checkbox from
                        // unchecking itself if you clicked it, even though
                        // the is_selected observable was just fine.
                        cust.is_selected.notifySubscribers(cust.is_selected());
                    });
                }
            });



            self.customizers.push(cust);
            //self.computed_quantity[product.code].internal_obs = internal_obs;
        });

        // Remove anything that isn't necessary anymore.
        _.each(_.filter(self.customizers(), function(cust) { return !cust.should_keep; }), function(cust) {
            self.customizers().remove(cust);
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

    self.select_row = function(cust, eargs) {
        console.log("You clicked a row.");

        if(eargs && eargs.preventDefault) {
            eargs.preventDefault();
            eargs.stopPropagation();
        }
        if(self.selected() !== cust) {
            self.selected(cust);
        }
    };


    return self;
}