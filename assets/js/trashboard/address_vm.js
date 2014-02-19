
AddressVM = function(master, which) {
    var self = new BaseSectionVM(master);
    self.which = which;

    self.name = which;

    var fields = {
        'street1': ko.observable(),
        'street2': ko.observable(),
        'city': ko.observable(),
        'state': ko.observable(),
        'country': ko.observable(),
        'zip': ko.observable()
    };

    _.each(fields, function(v,k) {
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
            'system_address': 'System Address'
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
        return state;
    });


    return self;
};