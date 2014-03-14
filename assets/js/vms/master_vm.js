


// initialize a view model from a blob
MasterVM = function() {
    // capture a new copy of UAS into MasterVM's closure
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't one
    // field types
    self.fields = {
        'agreement_id': tidyObservable(),
        'campaign': tidyObservable(),
        'pricetable_date': tidyObservable(),
        'email': tidyObservable(),
        'approved': tidyObservable(),
        'floorplan': tidyObservable(null),
        'install_method': tidyObservable(null),
        'property_type': tidyObservable(null),
        'credit_status': ko.observable(''),
        'promo_code': tidyObservable(),
        'ssn': tidyObservable(''),
        'dirty': ko.observable(false),

        'messages': ko.observableArray([]),
        'errors': ko.observableArray([]),
        'restrictions': ko.observableArray([])

    };

    _.each(self.fields, function(obs, fieldname) {
        self[fieldname] = obs;
    });


    self.cart = new Cart();
    self.customization_cart = new Cart();


    // variables computed from json responses
    // most of these are sugar for their return values
    // attempt to figure out what prices to display in the nav
    // XXX: get this out of ReviewVM

    self.vms = {
        //'initial_info': InitialInfoVM(self),

        'applicant': ApplicantVM(self, 'applicant'),
        'coapplicant': ApplicantVM(self, 'coapplicant'),

        'system_address': AddressVM(self, 'system_address'),
        'credit': null,

        'monitoring': MonitoringVM(self),

        'package': PackageVM(self),
        'alacarte': ALaCarteVM(self),
        'combo': ComboVM(self),
        'closing': ClosingVM(self),
        'shipping': ShippingVM(self),
        'review': ReviewVM(self)
    };
    self.vms.credit = CreditVM(self);

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

        // These are ord with null because selects are weird in ko
        agreement.floorplan = self.floorplan() || null;
        agreement.property_type = self.property_type() || null;
        agreement.install_method = self.install_method() || null;

        _.each(self.vms, function(vm) {
            vm.construct_agreement(agreement);
        });

        return agreement;
    };

    self.update_from_agreement = function(agreement, errors) {
        console.log("master update_from_agreement", agreement);

        self.email(agreement.email);
        self.campaign(agreement.campaign);
        self.pricetable_date(agreement.pricetable_date);
        self.promo_code(agreement.pricetable_date);

        // Credit status is read only
        self.credit_status(agreement.credit_status);

        self.floorplan(agreement.floorplan);
        self.property_type(agreement.property_type);
        self.install_method(agreement.install_method);

        if(agreement) {
            self.campaign(agreement.campaign);
            self.promo_code(agreement.promo_code);
            self.email(agreement.email);

            _.each(self.vms, function(vm) {
                vm.update_from_agreement(agreement);
            });
        }
        _.each(errors, function(error) {
            alert(error);
        });

        self.dirty(false);
        console.log("master update_from_agreement ended");
    };


    self.save_and_submit = function(vm, eargs) {
        if(eargs && eargs.preventDefault) {
            eargs.preventDefault();
        }

        var agreement_blob = self.construct_agreement();
        var data = agreement_endpoint._save(agreement_blob);
        window.master_blob = data;

        self.update_from_agreement(data.agreement, data.errors);
        catalog.update_catalog(data.catalog);

        _.each(data.messages, function(msg) {
            alert(msg);
        });

        _.each(data.errors, function(err) {
            alert(err);
        });

        self.messages(data.messages);
        self.errors(data.errors);
        self.restrictions(data.restrictions);


    }

    self.onCatalogUpdated = function() {
        self.cart.update_from_catalog();
        self.customization_cart.update_from_catalog();

        _.each(self.vms, function(vm) {
            vm.cart_trigger.valueHasMutated();
        });
    }



    // XXX: insert other fns above this line
    return self;
};

window.tidyCount = 0;

function tidyObservable(val) {
    var obs = ko.observable(val);
    //obs.tidy = window.tidyCount++;
    obs.subscribe(function(newValue) {
        if(!master.dirty()) {
            //console.log("Setting dirty for ", obs, newValue);
            //window.dirtything = obs;
            master.dirty(true);
        }
    });
    return obs;
}
