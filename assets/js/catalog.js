
Catalog = function() {
    var self = this;
    self.PRODUCTS = ko.observableArray([]);
    self.PRODUCTS_BY_CODE = {};

    self.update_catalog = function(catalog_blob) {

        // 1. Sync products in PRODUCTS and PRODUCTS_BY_CODE.

        _.each(self.PRODUCTS(), function(prod) {
            prod.should_keep = false;
        });
        _.each(catalog_blob.products, function(prod) {
            console.log("Syncing ", prod)
            var existing_prod = self.PRODUCTS_BY_CODE[prod.code];
            if(existing_prod) {
                _.extend(existing_prod, prod);
                prod.should_keep = true;

            } else {
                // Make a copy of the product from json.
                prod = _.omit(prod);
                prod.price = ko.observable(null);

                // Insert it into products and products by code.
                self.PRODUCTS.push(prod);
                self.PRODUCTS_BY_CODE[prod.code] = prod;

                // This too.
                prod.should_keep = true;
            }
        });

        // Remove anything from either that was not in the catalog blob.
        _.each(_.filter(self.PRODUCTS(), function(prod) {
            return !prod.should_keep;
        }), function(prod) {
            self.PRODUCTS.remove(prod);
            delete self.PRODUCTS_BY_CODE[prod.code];
        });

        // 2. the price list does not have to be observable.
        self.PRICES = catalog_blob.prices;

        // 3. Add prices into the products.
        _.each(self.PRODUCTS(), function(prod) {
            prod.price(self.PRICES[prod.code] || null);

        });

        // 4. Insert products into product contents.
        _.each(self.PRODUCTS(), function(prod) {
            _.each(prod.contents, function(pc) {
                pc.product = self.PRODUCTS_BY_CODE[pc.code];
            });
        });

        // Binding to expressions/functions that use these observables should trigger
        // re-renders when they change.  Downside: carts with lines that refer to these will
        // not auto-update by availability, because those are binding to a different list (of cart lineS)
        // not to the available products.  Instead, each vm needs its cart updated after the catalog is generated.

        // 5. Update all of master's vms with the catalog.
        if(window.master) {
            window.master.onCatalogUpdated();
        }
        /*if(window.master && window.master.vms) {
            _.each(window.master.vms, function(vm) {
                vm.update_cart_lines();
            });
        }*/
    };
};