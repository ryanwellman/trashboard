
CartLine = function(cart, product) {
    var cline = this;
    cline.cart = cart;


    // Make a new cline line.
    var internal_obs = tidyObservable(0);

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

    var fields = {
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

    _.each(fields, function(v, i) {
        cline[i] = v;
    });

    cline.customize_quantity = ko.computed({
        'read': quantity,
        'write': function(newval) {
            var reject = false;
            if(!/^(\d+|)$/.test(newval)) {
                reject = true;
            } else if(+newval < cline.min_quantity()) {
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

    cline.delta_fmted = ko.computed(function() {
        if(cline.quantity() == cline.base_quantity()) {
            return '';
        } else if (cline.quantity() > cline.base_quantity()) {
            return '+' + (cline.quantity() - cline.base_quantity());
        } else {
            return cline.quantity() - cline.base_quantity();
        }
    });


    cline.upfront_each_fmted = ko.computed(function() {
        if(!cline.price() || !cline.price().upfront_price)
            return '';
        return formatCurrency(cline.price().upfront_price);
    });
    cline.upfront_line_fmted = ko.computed(function() {
       if(!cline.quantity() || !cline.price() || !cline.price().upfront_price)
           return '';
       return formatCurrency(cline.price().upfront_price * cline.quantity());
    });
    cline.monthly_each_fmted = ko.computed(function() {
        if(!cline.price() || !cline.price().monthly_price)
            return '';
        return formatCurrency(cline.price().monthly_price) + '/mo';
    });
    cline.monthly_line_fmted = ko.computed(function() {
       if(!cline.quantity() || !cline.price() || !cline.price().monthly_price)
           return '';
       return formatCurrency(cline.price().monthly_price * cline.quantity()) + '/mo';
    });


    cline.customize_cb = ko.computed(function() {
        if(!cline.price()) return 0;
        return (cline.base_quantity() - cline.quantity()) * cline.price().cb_points;
    });

    cline.is_selected_for_vm = function(vm) {
        if(!vm.selected_computables) {
            vm.selected_computables = {};
        }
        if(!vm.selected_computables[cline.code]) {

            vm.selected_computables[cline.code] = ko.computed({
                'read': function() {

                    var i_s = vm.selected() === cline;
                    //console.log("Determining is_selected for ", cline.code, i_s);
                    return i_s
                },
                write: function(checked) {
                    if(checked) {
                        //console.log("Selecting package.");
                        vm.selected(cline);
                    } else if(!checked && vm.selected() === cline) {
                        //console.log("Deselecting package.");
                        cline.quantity(0);
                        vm.selected(null);


                    }
                    _.defer(function () {
                        // I have no idea why this is necessary.  No amount of
                        // stopping propagation would keep the checkbox from
                        // unchecking itself if you clicked it, even though
                        // the is_selected observable was just fine.

                        vm.selected_computables[cline.code].notifySubscribers(vm.selected_computables[cline.code]());
                    });
                }
            });
        }
        return vm.selected_computables[cline.code];
    }

}


Cart = function() {
    var self = this;

    this.cart_lines = ko.observableArray([]);

    this.update_from_catalog = function() {


        _.each(self.cart_lines(), function(cline) {
            cline.should_keep = false;
        });
        var existing = _.indexBy(self.cart_lines(), function(cline) {
            return cline.code;
        });


        _.each(catalog.PRODUCTS(), function(product) {
            /*if(!product.price()) {
                console.log("Skipping ", product, "because it has no product_price.");
                return;
            }*/
            var e = existing[product.code];
            if(e) {
                e.name=product.name;
                e.product = product;
                e.price(product.price());
                e.should_keep = true;
                return; //Having updated the prices we're done with this.

            }
            var cline = new CartLine(self, product);



            self.cart_lines.push(cline);
        });
    };

};