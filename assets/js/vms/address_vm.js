
AddressVM = function(master, which) {
    var self = new BaseSectionVM(master);
    self.which = which;

    self.name = which;

    self.fields = {
        'street1': tidyObservable(),
        'street2': tidyObservable(),
        'city': tidyObservable(),
        'state': tidyObservable(),
        'country': tidyObservable(),
        'zip': tidyObservable()
    };

    _.each(self.fields, function(v,k) {
        self[k] = v;
    });


    self.is_completed = ko.computed(function() {
        if(self.which === 'system_address' && !self.master.floorplan()) {
            //If I'm system address, I need floorplan chosen.
            return false;
        }
        return self.street1() && self.city() && self.state() && self.zip();
        // we can figure out what country you're in from the state
    });

    self.display_label = ko.computed(function() {
        return {
            'system_address': 'Address'
        }[self.name];
    });

    self.city_and_state = ko.computed(function() {
        var city = self.city();
        var state = self.state();

        var cs = city || '';
        if(state) {
            if(cs) {
                cs += ', ';
            }
            cs += state;
        }
        return cs;
    });

    self.update_from_agreement = function(agreement) {
        var person = agreement[self.which] || {};

        _.each(self.fields, function(obs, f) {
            obs(person[f] || '');
        });



    };

    self.construct_agreement = function(agreement) {
        var person = {};
        _.each(self.fields, function(obs, f) {
            person[f] = obs();
        });

        agreement[self.which] = person;

    };



    return self;
};
