
PackageVM = function(blob) {
    var self = new BaseSectionVM();
    blob = blob || {};

    var fields = {
        'selected_package': ko.observable,
        'customizing': ko.observable,
        'custom_quantities': Object,
        'cb_balance': ko.observable,
        'updated_contents': ko.observableArray,
        'changed_contents': ko.observable,
        'customization_lines': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // selected_package is another one of those special things that has
    // to come out of one of the window variables
    if(self.selected_package().code) {
        self['selected_package'](package_index[self.selected_package().code]);
    }

    // if there's no customization lines the customize button doesn't work
    // the customization lines need to be updated with quantities as well
    self.prepare_clines = function() {
        // fill the customization lines with available parts
        _.map(window.PRODUCTS_BY_TYPE.Part, function(part) {
            var cline= {
                code: part.code,
                part: part,
                quantity: ko.observable(0),
                min_quantity: ko.observable(0),
            };

            // subscribe this to cust_quantity_changed
            cline.quantity.subscribe(self.cust_quantity_changed);
            self.customization_lines.push(cline);
            cline.quantity.subscribe(self.cust_quantity_changed);
        });

        // now fill them with the correct quantities
        if(self.updated_contents().length && self.changed_contents()) {
            // did we pass in an updated package from the backend?
            _.each(self.updated_contents(), function(line) {
                // Find the customization line for that product
                var cline = _.find(self.customization_lines(), function(cline) {
                    return cline.code == line.code;
                });
                // Set that customization line's quantity and min quantity appropriately.
                if(cline) {
                    //console.log("Found matching cline, ", cline.quantity);
                    cline.quantity(line.quantity);
                    //TODO: Set min quantity
                } else {
                    //console.log("!Found matching cline", cline);
                }
            });
        } else if(self.selected_package().contents && self.selected_package().contents.length && !self.changed_contents()) {
            // deal with the regular package contents instead if not
            _.each(self.selected_package().contents, function(line) {
                // Find the customization line for that product
                var cline = _.find(self.customization_lines(), function(cline) {
                    return cline.code == line.code;
                });
                // Set that customization line's quantity and min quantity appropriately.
                if(cline) {
                    //console.log("Found matching cline, ", line.quantity);
                    cline.quantity(line.quantity);
                    //TODO: Set min quantity
                } else {
                    //console.log("!Found matching cline", cline);
                }
            });
        }
    };

    self.select_package = function(package) {
        if(self.done()) {
            return;
        }

        self.selected_package(package);
        self.custom_quantities = {};
        self.customization_lines.removeAll();
        // clear out any updated contents when selected package changes
        self.updated_contents([]);
        self.changed_contents(false);
        self.customizing(false);

        if(!self.customization_lines().length) {
            _.map(window.PRODUCTS_BY_TYPE.Part, function(part) {
                var cline= {
                    code: part.code,
                    part: part,
                    quantity: ko.observable(0),
                    min_quantity: ko.observable(0),
                };
                cline.quantity.subscribe(self.cust_quantity_changed);
                //console.log("Pushing new cline ", cline);
                self.customization_lines.push(cline);

                cline.quantity.subscribe(self.cust_quantity_changed);
            });
        }

        if(package) {
            // For each line of stuff that comes in the package normally,
            _.each(self.selected_package().contents, function(line) {
                // Find the customization line for that product
                var cline = _.find(self.customization_lines(), function(cline) {
                    return cline.code == line.code;
                });
                // Set that customization line's quantity and min quantity appropriately.
                if(cline) {
                    //console.log("Found matching cline, ", line.quantity);
                    cline.quantity(line.quantity);
                    //TODO: Set min quantity
                } else {
                    //console.log("!Found matching cline", cline);
                }
            });
        }
    };

    self.customize = function () {
        // this needs to unlock the form when you click it
        self.done(false);
        self.customizing(true);
    };

    self.cust_quantity_changed = function() {
        self.customization_deltas = [];
        var balance = 0;

        package_by_part = _.object(_.pluck(self.selected_package().contents, 'code'), self.selected_package().contents);
        clines_by_part = _.object(_.pluck(self.customization_lines(), 'code'), self.customization_lines());
        //console.log(clines_by_part);

        _.each(clines_by_part, function(cline,code) {
            var pline = package_by_part[code];
            var pq = 0;
            if (pline) {
                pq = pline.quantity;
            }

            var delta = cline.quantity() - pq;
            if(delta == 0)
                return;

            //console.log("I think that the cline for part ", code, " has ", cline.quantity(), "and the pline has ", pq);

            self.customization_deltas.push({
                code: code,
                delta: delta,
            });
        });
        //console.log("deltas", self.customization_deltas);
        //console.log("data", self.data_to_send);

        for (var i=0; i<self.customization_deltas.length; i++) {
            balance += -1 * (self.customization_deltas[i].delta * clines_by_part[self.customization_deltas[i].code].part.points);
        }
        self.cb_balance(balance);
    };

    self.selected_package_contents = function() {
        if(!self.selected_package()) {
            return [];
        }
        return self.selected_package().contents;
    }

    self.select_package_classes = function(param) {
        var classes = param.code;
        if(param === self.selected_package()) {
            classes += ' currently_chosen';
        }
        return classes;
    };

    self.save_package = function() {
        alert("Could now send this to server: " + self._serialize());
    };

    self.save_customization = function () {
        //clear any previous updated contents
        self.updated_contents([]);
        self.customized_parts = [];
        for (var i=0; i<self.customization_lines().length; i++) {
            if (self.customization_lines()[i].quantity() > 0) {
                self.c_parts = {};
                self.c_parts['code'] = self.customization_lines()[i].code;
                self.c_parts['quantity'] = self.customization_lines()[i].quantity();
                self.c_parts['part'] = self.customization_lines()[i].part;
                self.customized_parts.push(self.c_parts);
                self.updated_contents.push(self.c_parts);
            }
        }
        self.changed_contents(true);
        self.customizing(false);
        $('body').animate({
            scrollTop: $('#pkgsel').offset().top,
        }, 1000);
    };

    self.cancel_customization = function() {
        self.customizing(false);
        $('body').animate({
            scrollTop: $('#pkgsel').offset().top,
        }, 1000);
    };

    self._serialize = function() {
        ret = {
            'customizations': self.customization_deltas,
            'package': self.selected_package().code,
        };
        return JSON.stringify(ret);
    };

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear([self.selected_package]);
        self.done(false);
    };

    // this has to be at the bottom if a package is selected (saved in)
    self.prepare_clines();

    return self;
};
