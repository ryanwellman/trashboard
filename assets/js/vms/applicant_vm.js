
// refer to the comments in MasterVM to understand the next two objects
ApplicantVM = function(master, which) {
    var self = new BaseSectionVM(master);
    self.name = which;

    self.fields = {
        'first_name': tidyObservable(''),
        'last_name': tidyObservable(''),
        'initial': tidyObservable(''),
        'phone1': tidyObservable(''),
    };

    _.each(self.fields, function(v, k) {
        self[k] = v;
    });

    self.template_name = function() {
        return 'applicant_vm';
    };


    self.which = which; // Which is the field I am working with on the agreement (applicant, coapplicant)
    self.has_coapplicant = tidyObservable(false);


    self.is_completed = ko.computed(function() {
        if(self.which === 'coapplicant' && !self.has_coapplicant()) {
            return true;
        }
        return self.first_name() && self.last_name() && self.phone1() && self.master.email();
    });

    self.full_name = ko.computed(function() {
        var full_name = self.first_name();
        if(self.last_name()) {
            if(full_name) full_name += ' ';
            full_name += self.last_name();
        }
        return full_name;
    });


    self.display_label = function() {
        return self.which === 'applicant' ?
            'Applicant' : 'Coapplicant';
    };

    self.update_from_agreement = function(agreement) {
        var person = agreement[self.which];

        if(self.which === 'coapplicant'){
            self.has_coapplicant(!!person);
        }

        person = person || {};

        self.first_name(person.first_name || '');
        self.last_name(person.last_name || '');
        self.initial(person.initial || '');
        self.phone1(person.phone1 || '');

    };

    self.construct_agreement = function(agreement) {
        if(self.which === 'coapplicant' && ! self.has_coapplicant()) {
            return;
        }
        var person = {
            'first_name' : self.first_name(),
            'last_name': self.last_name(),
            'initial': self.initial(),
            'phone1': self.phone1()
        };

        agreement[self.which] = person;
    };

    return self;
}
