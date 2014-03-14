
// fix the window level vars for this to work
/* All this moved into catalog.js

_.each(window.PRODUCTS, function(prod) {
    // There is a price in the pricetable for this object so it is purchasable.
    // XXX: This might need to check that the price is not null, but I'm not sure just yet.
    prod.product_price = ko.observable(window.PRICES[prod.code]);
    prod.available = ko.computed(function() {
        return !!prod.product_price;
    });
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
*/

window.PROPERTY_TYPES = [
    'Residential',
    'Commercial'
];
window.FLOORPLANS = [
    'One Floor',
    'One Floor Split',
    'Two Floor'

];

// The truth is that none of this should really EVER change, other than adding and removing, right?
// So can I just.. not do this?

/*
Part = function(blob) {
    return {
        'code': ko.observable(blob.code),
        'category': ko.observable(blob.category),
        'product_type': ko.observable(blob.product_type),
    }
}
*/


// jquery on ready wrapper to anonymous function
$(function() {

    // Construct and fetch the current catalog.
    window.catalog = new Catalog();


    // create an object that knockout can use to bind
    window.master = new MasterVM();

    //catalog.update_catalog(InitialCatalogData);



    // Get the current agreement blob.
    agreement_endpoint = new AgreementEndpoint();
    master_blob = agreement_endpoint._load(window.agreement_id);

    catalog.update_catalog(master_blob.catalog);
    master.update_from_agreement(master_blob.agreement, []);


    // apply bindings for knockout
    ko.applyBindings(window.master, $('#master_vm')[0]);

    // SCROLL SPY

    // scrollspy to activate elements in the navbar when they are visible
    $('body').scrollspy({target: '#right_sidebar', offset: 150});


    // The applyBindings call has a side effect when there are observables bound to Select.  They call the observable and set it to undefined.
    master.dirty(false);
    return;


});

window.updateScrollspy = function() {
    $('body').scrollspy('refresh');
}
