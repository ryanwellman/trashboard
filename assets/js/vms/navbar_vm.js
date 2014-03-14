function NavBarVM(master) {
    var self = new BaseSectionVM(master);

    self.name = 'navbar';

    //console.log("Is window", self === window);
    return self;


    /*
    self.citystate = ko.computed(function() {
        return self.vms.billing_address.city() + (self.billing_address.state() ? ', ' + self.billing_address.state() : '');
    });

    self.countrysafe = ko.computed(function() {
        return self.vms.billing_address.country() || '';
    });


    // computed variables for the nav bar & review section
    self.agreement_id_nav = ko.computed(function() {
        return (self.master.agreement_id() || "No Agreement ID");
    });

    self.package_nav = ko.computed(function() {
        var p = self.master.package.selected_package();
        if(!p) {
            return 'No Package';
        }
        return p.name
    });

    self.monitoring_nav = ko.computed(function() {
        var m = self.master.monitoring.selected_monitoring();
        if(!m) {
            return 'No monitoring';
        }
        return m.name;

    });

    self.shipping_nav = ko.computed(function() {
        var m = self.master.shipping.selected_shipping();
        if(!m) {
            return 'No shipping';
        }
        return m.name;

    });

    self.cb_balance = ko.computed(function() {
        return self.master.package.cb_balance();
    });

    */


}