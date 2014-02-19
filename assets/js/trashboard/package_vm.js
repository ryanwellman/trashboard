
PackageVM = function(master) {
    var self = new BaseSectionVM(master);
    self.name = 'package';
    var fields = {
        'selected': ko.observable(null),

        'custom_quantities': {},
        'updated_contents': ko.observableArray(),
        'changed_contents': ko.observable(),
        'customization_lines': ko.observableArray(),
    };



    // copy them out of fields onto this itself.
    _.each(fields, function(v, k) {
         self[k] = v;
    });


    self.is_completed = ko.computed(function() {
        return !!self.selected() && !self.customizing();
    });

    self.available_products = function() {
        return window.PRODUCTS_BY_TYPE.Part;
    }

    self.generate_customizers();


    self.select_package = function(package) {

        self.selected(package);

        self.reset_customizations();
    };

    self.reset_customizations = function() {
        var package = self.selected();
        var contents = {};
        if(package) {
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


    // Package is priced differently than most things.
    self.monthly_subtotal = ko.computed(function() {
        if(!self.selected())
            return 0;
        return self.selected().product_price.monthly_price;
    });

    self.upfront_subtotal = ko.computed(function() {
        if(!self.selected())
            return 0;
        return self.selected().product_price.upfront_price;
    });

    self.cb_balance = ko.computed(function() {
        var total_balance = 0;
        _.each(self.customizers(), function(cust) {
            total_balance += (cust.base_quantity() - cust.quantity()) * cust.price.cb_points;
        });
        return total_balance;
    });


    self.choose_package = self.select_package;

    self.customize = function () {
        // this needs to unlock the form when you click it
        self.customizing(true);
    };


    return self;
};
