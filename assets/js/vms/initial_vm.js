function InitialInfoVM(master) {
    var self = new BaseSectionVM(master);
    self.name = 'initial_info';

    self.billing_address_zip = ko.observable();
    self.floorplan = ko.observable();

    // initial info section
    self.is_completed = ko.computed(function() {
        return self.billing_address_zip() && self.floorplan();
    });

    self.display_label = function() {
        return 'Initial Information';
    }

    return self;

}