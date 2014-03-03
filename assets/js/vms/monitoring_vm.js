function MonitoringVM(master) {
    var self = new BaseSectionVM(master);
    self.name = 'monitoring';

    var fields = {

    };

    _.each(fields, function(v, k) {
        self[k] = v;
    });




    self.available_products = ko.computed(function() {
        return _.filter(window.catalog.PRODUCTS(), function(prod) {
            return prod.price() && prod.product_type === 'Monitoring';
        });
    });

    self.is_completed = ko.computed(function() {
        return !!self.selected();
    });

    self.select_monitoring = function(cline) {
        self.selected(cline);
    }


    self.monitoring_css = function(cline) {
        var classes = ['monitoring', cline.product.code];
        if(cline === self.selected()) {
             classes.push('selected');
        }
        return classes.join(' ');
    }



    return self;

}
