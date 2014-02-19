function MonitoringVM(master) {
    var self = new BaseSectionVM(master);
    self.name = 'monitoring';

    var fields = {
        'selected': ko.observable(null),
    };

    _.each(fields, function(v, k) {
        self[k] = v;
    });

    self.is_completed = ko.computed(function() {
        return !!self.selected();
    });


    return self;

}