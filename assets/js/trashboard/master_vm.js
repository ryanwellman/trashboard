


// initialize a view model from a blob
MasterVM = function(blob) {
    // capture a new copy of UAS into MasterVM's closure
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't one
    blob = blob || {};

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
    };

    _.each(self.fields, function(obs, fieldname) {
        self[fieldname] = obs;
    });

    // variables computed from json responses
    // most of these are sugar for their return values
    // attempt to figure out what prices to display in the nav
    // XXX: get this out of ReviewVM

    self.vms = {
        'initial_info': InitialInfoVM(self),
        'shipping': ShippingVM(self),
        'applicant': ApplicantVM(self, 'applicant'),
        'coapplicant': ApplicantVM(self, 'coapplicant'),
        'monitoring': MonitoringVM(self),
        'package': PackageVM(self),
        'system_address': AddressVM(self, 'system_address'),
        'combo': ComboVM(self),
        'alacarte': ALaCarteVM(self),
        'closing': ClosingVM(self),
        'review': ReviewVM(self)
    };

    self.vms['navbar'] = NavBarVM(self);



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




/*
    self.test_initialinfo = function() {
        // test completeness and set flag
        if(self.initial_complete()) {
            self._next('#initial_info', '#pkgsel, #nav_pkgsel', '#pkgsel');
        }
    };


self.clear_initialinfo = function() {
    // clear initial info fields in viewmodel
    self.billing_address.zip('');
    self.floorplan('');
    self.promo_code('');
};

self.test_cinfo = function() {
    // test completeness and set flag
    if(self.cinfo_complete()) {
        self._next('#cinfo', '#shipping, #nav_shipping', '#shipping');
    }
};

self.clear_cinfo = function() {
    // clear cinfo fields in viewmodel
    self.applicant.clear();
    self.billing_address.clear();
    self.email('');
};

self.test_pkgsel = function() {
    // test completeness and set flag
    if(self.package.complete()) {
        self._next('#pkgsel', '#monitor, #nav_monitor', '#monitor');
    }
};

self.clear_pkgsel = function() {
    // clear package field in viewmodel
    self.package.clear();
};

self.test_monitor = function() {
    // test completeness and set flag
    if(self.monitoring()) {
        self._next('#monitor', '#premium, #nav_premium', '#premium');
    }
};

self.clear_monitor = function() {
    // clear monitoring field in viewmodel
    self.monitoring('');
};

self.test_premium = function() {
    // test completeness with flag since this is open-ended
    if(self.premium.complete()) {
        self._next('#premium', '#combos, #nav_combos', '#combos');
    }
};

self.clear_premium = function() {
    self.premium.clear();
};

self.test_combo = function() {
    // test completeness with flag since this is open-ended
    if(self.combo.complete()) {
        self._next('#combos', '#a_la_carte, #nav_a_la_carte', '#a_la_carte');
    }
};

self.clear_combo = function() {
    self.combo.clear();
};

self.test_alacarte = function() {
    // test completeness with flag since this is open-ended
    if(self.alacarte.complete()) {
        self._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos', '#services');
    }
};

self.clear_alacarte = function() {
    self.alacarte.clear();
};

self.test_services_and_promos = function() {
    if(self.services_and_promos.done()) {
        self._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo', '#cinfo');
    }
};

self.test_shipping = function() {
    // test completeness and set flag
    if(self.shipping()) {
        self._next('#shipping', '#closing, #nav_closing', '#closing');
    }
};

self.clear_shipping = function() {
    self.shipping('');
};

self.test_closing = function() {
    // test completeness with flag since this is open-ended
    if(self.closing.complete()) {
        self._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller', '#review');
    }
};

self.clear_closing = function() {
    self.closing.clear();
};
    */





    // XXX: insert other fns above this line
    return self;
};