function ShippingVM(master) {
    var self = new UpdatableAndSerializable();

    self.master = master;



    self.selected_shipping = function(shipp) {
        self.shipping(shipp.value);
    };

    self.shipcss = function(param) {
        return param.code == self.shipping() ? 'currently_chosen' : '';
    };


}