

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

    self.cart_lines = ko.computed(function() {
        self.cart_trigger();

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



    return self;
};

