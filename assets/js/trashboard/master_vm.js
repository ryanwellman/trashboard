


// initialize a view model from a blob
MasterVM = function() {
    // capture a new copy of UAS into MasterVM's closure
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't one
    // field types
    self.fields = {
        'agreement_id': ko.observable(),
        'pricetable_date': ko.observable(),
        'email': ko.observable(),
        'approved': ko.observable(),
        'shipping': ko.observable(),
        'monitoring': ko.observable(),
        'email': ko.observable(),
        'floorplan': ko.observable(),
        'promo_code': ko.observable(),
        'ssn': ko.observable('')
    };

    _.each(self.fields, function(obs, fieldname) {
        self[fieldname] = obs;
    });

    // variables computed from json responses
    // most of these are sugar for their return values
    // attempt to figure out what prices to display in the nav
    // XXX: get this out of ReviewVM

    self.vms = {
        //'initial_info': InitialInfoVM(self),
        /*'shipping': ShippingVM(self), */
        'applicant': ApplicantVM(self, 'applicant'),
        'coapplicant': ApplicantVM(self, 'coapplicant'),

        'system_address': AddressVM(self, 'system_address'),

        'monitoring': MonitoringVM(self),

        'package': PackageVM(self),
        'alacarte': ALaCarteVM(self),
        'closing': ClosingVM(self),

        /*
        'combo': ComboVM(self),
        'review': ReviewVM(self)*/
    };

    self.navbar = new NavBarVM(self);

    self.cb_balance = ko.computed(function() {
        var total_balance = 0;
        _.each(self.vms, function(vm) {
            total_balance += vm.cb_balance();
        });
        return total_balance;
    });

    self.upfront_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.vms, function(vm) {
            total_balance += vm.upfront_subtotal();

        });
        return total_balance;
    });

    self.monthly_subtotal = ko.computed(function() {
        var total_balance = 0;
        _.each(self.vms, function(vm) {
            total_balance += vm.monthly_subtotal();
        });
        return total_balance;
    });





    self.construct_agreement = function() {
        agreement = {
            'applicant': null,
            'coapplicant': null,
            'billing_address': null,
            'campaign': null,
            'date_updated': null,
            'email': null,
            'invoice_lines': [],
            'pricetable_date': null,
            'promo_code': null,
            'system_address': null,
            'agreement_id': null,

        };

        agreement.agreement_id = self.agreement_id();
        agreement.email = self.email();
        agreement.campaign = self.campaign();
        agreement.pricetable_date = self.pricetable_date();
        agreement.promo_code = self.promo_code();

        _.each(self.vms, function(vm) {
            vm.construct_agreement(agreement);
        });

        return agreement;
    };





    // XXX: insert other fns above this line
    return self;
};