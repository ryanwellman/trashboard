
// refer to the comments in MasterVM to understand the next two objects
CreditVM = function(master) {
    var self = new BaseSectionVM(master);
    self.name = 'credit';

    function field_subset(which){
        var cf = {
            'person_id': ko.observable(),
            'credit_status': ko.observable(),
            'social': tidyObservable(''),
            'first_name': master.vms[which].first_name,
            'last_name': master.vms[which].last_name
        };
        cf.should_show = ko.computed(function() {
            if(which === 'coapplicant') {
                return master.vms.coapplicant.has_coapplicant();
            } else {
                return master.vms.applicant.first_name() || master.vms.applicant.last_name();
            }
        });
        cf.which = which.substring(0,1).toUpperCase() + which.substring(1);
        cf.label_display_text = ko.computed(function(){
            var status = cf.credit_status();

            if(!status){
                status = 'NOT RUN';
            }

            // jQuery object to string
            var icon = $("<i/>", {
                'class': window.CREDIT_LABEL_ICON_OPTIONS[status]
            }).wrap('<div/>').parent().html();

            return icon + " " + status;
        });
        cf.label_display = ko.computed(function(){
            var status = cf.credit_status();

            if(!status){
                status = 'NOT RUN';
            }

            return window.CREDIT_LABEL_OPTIONS[status];
        });
        return cf;
    }
    self.applicant_credit = field_subset('applicant');
    self.coapplicant_credit = field_subset('coapplicant');
    self.agreement_credit = ko.observable();


    self.template_name = function() {
        return 'credit_vm';
    };

    // Borrowing this observable for brevity.
    self.has_coapplicant = master.vms.coapplicant.has_coapplicant;

    self.is_completed = ko.computed(function() {
        return self.agreement_credit() === 'APPROVED' || self.agreement_credit() === 'DCS';
    });

    self.display_label = function() {
        return 'Credit';
    };

    self.update_from_agreement = function(agreement) {
        function sub_update(which, blob) {
            if(blob) {
                which.person_id(blob.person_id);
                which.credit_status(blob.credit_status);
                if(which.person_id()) {
                    which.social('');
                }
            }
        }
        sub_update(self.applicant_credit, agreement.applicant);
        sub_update(self.coapplicant_credit, agreement.coapplicant);
        self.agreement_credit(agreement.credit_status);

    };

    self.construct_agreement = function(agreement) {
        // Send the socials with the applicants, if they were entered.
        if(agreement.applicant && self.applicant_credit.social()) {
            agreement.applicant.social = self.applicant_credit.social();
        }
        if(agreement.coapplicant && self.coapplicant_credit.social()) {
            agreement.coapplicant.social = self.coapplicant_credit.social();
        }
    };

    return self;
}
