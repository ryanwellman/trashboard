
// refer to the comments in MasterVM to understand the next two objects
ApplicantVM = function(master, which) {
    var self = new BaseSectionVM(master);
    self.name = 'applicant';

    var fields = {
        'fname': ko.observable(''),
        'lname': ko.observable(''),
        'initial': ko.observable(''),
        'phone': ko.observable(''),
    };

    _.each(fields, function(v, k) {
        self[k] = v;
    });

    self.which = which; // Which is the field I am working with on the agreement (applicant, coapplicant)

    self.is_completed = ko.computed(function() {
        return self.fname() && self.lname() && self.phone();
    });

    self.full_name = ko.computed(function() {
        var full_name = self.fname();
        if(self.lname()) {
            if(full_name) full_name += ' ';
            full_name += self.lname();
        }
        return full_name;
    });

    return self;
}