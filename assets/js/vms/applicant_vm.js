
// refer to the comments in MasterVM to understand the next two objects
ApplicantVM = function(master, which) {
    var self = new BaseSectionVM(master);
    self.name = which;

    self.fields = {
        'fname': ko.observable(''),
        'lname': ko.observable(''),
        'initial': ko.observable(''),
        'phone1': ko.observable(''),
    };

    _.each(self.fields, function(v, k) {
        self[k] = v;
    });

    self.template_name = function() {
        return 'applicant_vm';
    };


    self.which = which; // Which is the field I am working with on the agreement (applicant, coapplicant)
    self.has_coapplicant = ko.observable(false);


    self.is_completed = ko.computed(function() {
        if(self.which === 'coapplicant' && !self.has_coapplicant()) {
            return true;
        }
        return self.fname() && self.lname() && self.phone1() && self.master.email() && self.master.ssn();
    });

    self.full_name = ko.computed(function() {
        var full_name = self.fname();
        if(self.lname()) {
            if(full_name) full_name += ' ';
            full_name += self.lname();
        }
        return full_name;
    });


    self.display_label = function() {
        return self.which === 'applicant' ?
            'Applicant' : 'Coapplicant';
    };

    self.update_from_agreement = function(agreement) {
        var person = agreement[self.which] || {};

        self.fname(person.fname || '');
        self.lname(person.lname || '');
        self.initial(person.initial || '');
        self.phone1(person.phone1 || '');

    };

    self.construct_agreement = function(agreement) {
        var person = {
            'fname' : self.fname(),
            'lname': self.lname(),
            'initial': self.initial(),
            'phone1': self.phone1()
        };

        agreement[self.which] = person;
    };

    return self;
}