
// fix the window level vars for this to work
_.each(window.PRODUCTS, function(prod) {
    // There is a price in the pricetable for this object so it is purchasable.
    // XXX: This might need to check that the price is not null, but I'm not sure just yet.
    prod.product_price = window.PRICES[prod.code];
    prod.available = !!prod.product_price;
});

//P_B_T['Part'] = [Part, Part, Part];
window.PRODUCTS_BY_TYPE = _.groupBy(window.PRODUCTS, function(prod) {
    return prod.product_type;
});

// All products with subproducts need to be merged in appropriately.
_.each(window.PRODUCTS, function(prod) {
    if(!prod.contents || !prod.contents.length) {
        return; // Skip anything that has no contents.
    }
    // Then go over each productcontent in it.
    _.each(prod.contents, function(pc) {
        // This has quantity, maybe some price info, but specifically a product that
        // is included.  Replace the product with a reference.
        pc.product = window.PRODUCTS[pc.code];
    });
});

// jquery on ready wrapper to anonymous function
$(function() {

    // create an object that knockout can use to bind
    agreement_endpoint = new AgreementEndpoint();
    master_blob = agreement_endpoint._load();
    window.master = new MasterVM();




    // apply bindings for knockout
    ko.applyBindings(window.master, $('#master_vm')[0]);

    // SCROLL SPY

    // scrollspy to activate elements in the navbar when they are visible
    $('body').scrollspy({target: '#right_sidebar', offset: 150});


    return;


});
