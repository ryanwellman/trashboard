
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
    ko.applyBindings(window.master);

    // SCROLL SPY

    // scrollspy to activate elements in the navbar when they are visible
    $('body').scrollspy({target: '#right_sidebar', offset: 150});


    return;

    /*

    // JQUERY FORM-SPECIFIC MANIPS

    // customer info
    // select the correct credit button
    var credit_str = "<a class='btn btn-large ";
    if (window.master.approved()) {
        if (window.master.approved() == 'approved') { credit_str += "btn-success'><i class='icon-ok icon-white'></i> Approved</a>"; };
        if (window.master.approved() == 'dcs') { credit_str += "btn-danger'><i class='icon-remove icon-white'></i> Approved DCS</a>"; };
        if (window.master.approved() == 'no hit') { credit_str += "btn-warning'><i class='icon-warning-sign icon-white'></i> No Hit</a>"; };
        $('#credit_btn').empty().append(credit_str);
    }


    // FORM LOGIC

    // test all the sections for completeness and move us to the correct spot
    checklist = [window.master.initial_complete(), window.master.package.complete(), window.master.cinfo_complete(), window.master.monitoring(), window.master.premium.complete(), window.master.combo.complete(), window.master.alacarte.complete(), window.master.services_and_promos.done(), window.master.shipping(), window.master.closing.complete()];
    first_incomplete = _.reduce(checklist, function(memo, value) { return (value) ? memo + 1 : memo; }, 0); // cannot complete a section w/o clicking next on the one above it

    // reveal the sections up to whichever one is behind
    switch(first_incomplete) {
        case 10:
            window.master._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller');
            window.master._hide('#closing_form');
        case 9:
            window.master._next('#shipping', '#closing, #nav_closing');
            window.master._hide('#shipping_form');
        case 8:
            window.master._next('#cinfo', '#shipping, #nav_shipping');
            window.master._hide('#cinfo_form');
        case 7:
            window.master._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo');
            window.master._hide('#promo_form');
        case 6:
            window.master._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos');
            window.master._hide('#alacarte_form');
        case 5:
            window.master._next('#combos', '#a_la_carte, #nav_a_la_carte');
            window.master._hide('#combo_form');
        case 4:
            window.master._next('#premium', '#combos, #nav_combos');
            window.master._hide('#premium_form');
        case 3:
            window.master._next('#monitor', '#premium, #nav_premium');
            window.master._hide('#monitor_form');
        case 2:
            window.master._next('#pkgsel', '#monitor, #nav_monitor');
            window.master._hide('#pkgsel_form');
        case 1:
            window.master._next('#initial_info', '#pkgsel, #nav_pkgsel');
            window.master._hide('#initialinfo_form');
        default:
            break;
    }

    // now do the actual animation
    switch(first_incomplete) {
        default:
            break;
        case 1: // initial info
            window.master._next('#initial_info', '#pkgsel, #nav_pkgsel', '#pkgsel');
            break;
        case 2: // package select
            window.master._next('#pkgsel', '#monitor, #nav_monitor', '#monitor');
            break;
        case 3: // monitoring
            window.master._next('#monitor', '#premium, #nav_premium', '#premium');
            break;
        case 4: // premium items
            window.master._next('#premium', '#combos, #nav_combos', '#combos');
            break;
        case 5: // combos
            window.master._next('#combos', '#a_la_carte, #nav_a_la_carte', '#a_la_carte');
            break;
        case 6: // a la carte
            window.master._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos', '#services');
            break;
        case 7: // services and promos
            window.master._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo', '#cinfo');
            break;
        case 8: // customer info
            window.master._next('#cinfo', '#shipping, #nav_shipping', '#shipping');
            break;
        case 9: // shipping
            window.master._next('#shipping', '#closing, #nav_closing', '#closing');
            break;
        case 10: // closing
            window.master._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller', '#review');
            break;
    }

    // form section button handlers

    // initial info
    $('#initialinfo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // fire test and save the viewmodel contents
        window.master.test_initialinfo();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#initialinfo_form');

        // at this point an agreement id has been assigned, so obtain it
        // XXX: get the entire thing loaded into window.master
        //      using the _update_from_dict() in UAS
        //blob = agreement_endpoint._load(window.master);
        //window.master._update_from_dict(blob); // doesn't actually work for some reason
    });
    $('#initialinfo_form').on('reset', function(evt) {
        // knockout does not refresh observables on a reset
        // so old values stay in the viewmodel but the fields
        // are all blank
        window.master.clear_initialinfo();
    });

    // customer info
    $('#cinfo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // fire test and save the viewmodel contents
        window.master.test_cinfo();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#cinfo_form');
    });
    $('#cinfo_form').on('reset', function(evt) {
        // knockout does not refresh observables on a reset
        // so old values stay in the viewmodel but the fields
        // are all blank
        window.master.clear_cinfo();
    });

    // package select
    $('#pkgsel_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.package.done(true);
        window.master.test_pkgsel();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#pkgsel_form');
    });
    $('#pkgsel_form').on('reset', function(evt) {
        // blank out package selection
        window.master.clear_pkgsel();
    });

    // monitoring
    $('#monitor_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.test_monitor();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#monitor_form');
    });
    $('#monitor_form').on('reset', function(evt) {
        // blank out monitoring selection
        window.master.clear_monitor();
    });

    // premium addons
    $('#premium_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.premium.done(true);
        window.master.test_premium();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#premium_form');
    });

    $('#premium_form').on('reset', function(evt) {
        // blank out premium items selection
        window.master.clear_premium();
    });

    // combos
    $('#combo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.combo.done(true);
        window.master.test_combo();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#combo_form');
    });
    $('#combo_form').on('reset', function(evt) {
        // blank out combo selection
        window.master.clear_combo();
    });

    // alacarte
    $('#alacarte_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.alacarte.done(true);
        window.master.test_alacarte();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#alacarte_form');
    });

    $('#alacarte_form').on('reset', function(evt) {
        // blank out alacarte selection
        window.master.clear_alacarte();
    });

    // promo and services
    $('#promo_form').on('submit', function(evt) {
        evt.preventDefault();

        window.master.services_and_promos.done(true);
        window.master.test_services_and_promos();

        // hide the buttons
        window.master._hide('#promo_form');
    });

    // shipping
    $('#shipping_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.test_shipping();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#shipping_form');
    });
    $('#shipping_form').on('reset', function(evt) {
        // blank out shipping selection
        window.master.clear_shipping();
    });

    // closing
    $('#closing_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        window.master.closing.done(true);
        window.master.test_closing();
        agreement_endpoint._save(window.master);

        // hide the buttons
        window.master._hide('#closing_form');
    });
    $('#closing_form').on('reset', function(evt) {
        // blank out closing selection
        window.master.clear_closing();
    });
    $('#global_save_btn').on('click', function(evt) {
        // just save without checking anything
        agreement_endpoint._save(window.master);
    });

*/
});
