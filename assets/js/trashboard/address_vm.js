
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
        return self.street1() && self.city() && self.state() && self.zip();
        // we can figure out what country you're in from the state
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