function InitialInfoVM(master) {
    var self = new BaseSectionVM('initial_info', master);

    // initial info section
    self.complete = function() {
        return self._test([self.billing_address.zip(), self.floorplan()]);
    };

    return self;

}