function MonitoringVM(master) {
    var self = new UpdatableAndSerializable();

    self.master = master;

    // this function will set the selected monitoring value
    self.selected_monitoring = function(monit) {
        self.monitoring(monit.value);
    };

    self.moncss = function(param) {
        return param.code == self.monitoring() ? 'currently_chosen' : '';
    };

        self.selected_shipping = function(shipp) {
        self.shipping(shipp.value);
    };

}