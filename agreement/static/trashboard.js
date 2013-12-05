// capture agreement_id from django if it was passed in
var agreement_id = window.AID.agreement_id;

// money formatting function
function formatCurrency(value) {
    return value.toFixed(2);
};

// KNOCKOUT VIEW MODELS

// first some utility objects

UpdatableAndSerializable = function() {
    // do not capture this into closure as self
    // this mixin uses 'parasitic' inheritance since the vm
    // constructors all start from a new UAS

    // this fn updates the view model from a blob
    // not as good as the python version
    this._update_from_dict = function(blob) {
        _.each(blob, function(v, k) {
            if(this.fields[k] === ko.observable) {
                // use observables as functions
                this[k](blob[k]);
            } else {
                // recursive viewmodel updates
                this[k]._update_from_dict(blob[k]);
            }
        });
    };

    // this fn returns a json-like blob from a view model
    // better than the python version by far
    this._serialize = function() {
        return ko.toJSON(this);
    };

    return this;
};

JSONHandler = function() {
    // this thing handles loading and saving json-like things to the
    // restful interface

    // capture this into JSONHandler's closure
    var self = this;

    // this fn obtains a json blob from the restful(?) interface
    self._load = function() {
        // obtain a payload
        payload = {};

        // obtain blob from ajax
        var result = $.ajax({
            dataType: "json",
            url: '/json3/' + agreement_id,
            async: false, // asynchronous load means empty blob
        });

        // log failure
        result.fail(function(xhr, status, error) {
            console.log('failed! (' + error + ') ' + status);
            console.log(xhr.responseText);
        });

        // log success
        result.done(function(data) {
            payload = data;
            console.log("loaded json" + (agreement_id ? " from agreement " + agreement_id : ''));
            console.log(ko.toJSON(data))
        });

        return payload;
    };

    // this fn allegedly saves the contents of obj
    // XXX: needs to be better
    self._save = function(obj) {
        // obtain a payload
        payload = ko.toJSON(obj);

        var result = $.ajax({
            type: "POST",
            dataType: "json",
            url: '/json3/' + agreement_id,
            async: false, // testing with and without this
            data: payload,
        });

        result.fail(function(xhr, status, error) {
            console.log('failed! (' + error + ') ' + status);
            console.log(xhr.responseText);
        });

        result.done(function(data) {
            // obtain that agreement id from the json response
            obj.id = data.id;
            console.log(data);
            console.log("saved json" + (agreement_id ? " to agreement " + agreement_id : '') + "\n" + ko.toJSON(self));
        });
    };
};

// refer to the comments in MasterVM to understand the next two objects
ApplicantVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'fname': ko.observable,
        'lname': ko.observable,
        'initial': ko.observable,
        'phone': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    return self;
};

AddressVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'address': ko.observable,
        'city': ko.observable,
        'state': ko.observable,
        'country': ko.observable,
        'zip': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    return self;
};

// this is ryan's vm for packages translated to the new style
// new PackageVM({'selected_package': null, 'customizing': false, 'cb_balance': 0, 'updated_contents': [], 'changed_contents': false, 'customization_lines': []})

// fix the window level vars for this to work
window.package_index = _.object(_.pluck(window.PACKAGES, 'code'), window.PACKAGES);
window.part_index = _.object(_.pluck(window.PARTS, 'code'), window.PARTS);

_.each(window.PACKAGES, function(package) {
    _.each(package.contents, function(line) {
        line.part = window.part_index[line.code];
    });
});

PackageVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_package': ko.observable,
        'customizing': ko.observable,
        'custom_quantities': Object,
        'cb_balance': ko.observable,
        'updated_contents': ko.observableArray,
        'changed_contents': ko.observable,
        'customization_lines': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.select_package = function(package) {
        if(self.done()) {
            return;
        }

        console.log("select customizing", self.customizing());
        self.selected_package(package);
        self.custom_quantities = {};
        self.customization_lines.removeAll();
        // clear out any updated contents when selected package changes
        self.updated_contents([]);
        self.changed_contents(false);
        self.customizing(false);

        if(!self.customization_lines().length) {
            _.map(window.PARTS, function(part) {
                var cline= {
                    code: part.code,
                    part: part,
                    quantity: ko.observable(0),
                    min_quantity: ko.observable(0),
                };
                cline.quantity.subscribe(self.cust_quantity_changed);
                //console.log("Pushing new cline ", cline);
                self.customization_lines.push(cline);

                cline.quantity.subscribe(self.cust_quantity_changed);
            });
        }

        if(package) {
            // For each line of stuff that comes in the package normally,
            _.each(self.selected_package().contents, function(line) {
                // Find the customization line for that product
                var cline = _.find(self.customization_lines(), function(cline) {
                    return cline.code == line.code;
                });
                // Set that customization line's quantity and min quantity appropriately.
                if(cline) {
                    //console.log("Found matching cline, ", line.quantity);
                    cline.quantity(line.quantity);
                    //TODO: Set min quantity
                } else {
                    //console.log("!Found matching cline", cline);
                }
            });
        }
    };

    self.customize = function () {
        self.customizing(true);
    };

    self.cust_quantity_changed = function() {
        self.customization_deltas = [];
        var balance = 0;

        package_by_part = _.object(_.pluck(self.selected_package().contents, 'code'), self.selected_package().contents);
        clines_by_part = _.object(_.pluck(self.customization_lines(), 'code'), self.customization_lines());
        //console.log(clines_by_part);

        _.each(clines_by_part, function(cline,code) {
            var pline = package_by_part[code];
            var pq = 0;
            if (pline) {
                pq = pline.quantity;
            }

            var delta = cline.quantity() - pq;
            if(delta == 0)
                return;

            //console.log("I think that the cline for part ", code, " has ", cline.quantity(), "and the pline has ", pq);

            self.customization_deltas.push({
                code: code,
                delta: delta,
            });
        });
        //console.log("deltas", self.customization_deltas);
        //console.log("data", self.data_to_send);

        for (var i=0; i<self.customization_deltas.length; i++) {
            balance += -1 * (self.customization_deltas[i].delta * clines_by_part[self.customization_deltas[i].code].part.points);
        }
        self.cb_balance(balance);
    };

    self.selected_package_contents = function() {
        if(!self.selected_package()) {
            return [];
        }
        return self.selected_package().contents;
    }

    self.select_package_classes = function(param) {
        var classes = param.code;
        if(param === self.selected_package()) {
            classes += ' currently_chosen';
        }
        return classes;
    };

    self.save_package = function() {
        alert("Could now send this to server: " + self._serialize());
    };

    self.save_customization = function () {
        //clear any previous updated contents
        self.updated_contents([]);
        self.customized_parts = [];
        for (var i=0; i<self.customization_lines().length; i++) {
            if (self.customization_lines()[i].quantity() > 0) {
                self.c_parts = {};
                self.c_parts['code'] = self.customization_lines()[i].code;
                self.c_parts['quantity'] = self.customization_lines()[i].quantity();
                self.c_parts['part'] = self.customization_lines()[i].part;
                self.customized_parts.push(self.c_parts);
                self.updated_contents.push(self.c_parts);
            }
        }
        self.changed_contents(true);
        self.customizing(false);
    };

    self.cancel_customization = function() {
        self.customizing(false);
    };

    self._serialize = function() {
        ret = {
            'customizations': self.customization_deltas,
            'package': self.selected_package().code,
        };
        return JSON.stringify(ret);
    };

    // hax: don't be done until a package is selected for the first time
    var flag = self.done();
    self.done(false);
    self.select_package(package_index[self.selected_package().code]);
    self.done(flag);
    return self;
};

PremiumVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_codes': ko.observableArray,
        'contents': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.select_item = function() {
        self.contents.removeAll();
        for(var i = 0; i < self.selected_codes().length; i++) {
            console.log(self.selected_codes()[i].contents);
            for(var j = 0; j < self.selected_codes()[i].contents.length; j++) {
                var ret = {
                    'code': self.selected_codes()[i].contents[j].code,
                    'quantity': self.selected_codes()[i].contents[j].quantity,
                };

                self.contents.push(ret);                            
            }
        }

        // required for ko to allow checkbox to click
        return true;
    };

    return self;
};

ComboVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_codes': ko.observableArray,
        'contents': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    self.select_item = function() {
        self.contents.removeAll();
        for(var i = 0; i < self.selected_codes().length; i++) {
            console.log(self.selected_codes()[i].contents);
            for(var j = 0; j < self.selected_codes()[i].contents.length; j++) {
                var ret = {
                    'code': self.selected_codes()[i].contents[j].code,
                    'quantity': self.selected_codes()[i].contents[j].quantity,
                };

                self.contents.push(ret);                            
            }
        }

        // required for ko to allow checkbox to click
        return true;
    };

    return self;
};

// next two view models are for customize
PartVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "category": ko.observable,
        "code": ko.observable,
        "name": ko.observable,
        "price": ko.observable,
        "points": ko.observable,
    }

    _.each(fields, function(v, k) {
        self[k] = v(blob[k]);
    });

    self.returnFields = function() {
        return fields;
    };

    return self;
};

PartLineVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "selected_part": PartVM,
        "quantity": ko.observable,
    };

    _.each(fields, function(v, k) {
        // cheating
        self[k] = ko.observable(blob[k])
        //self[k] = v(blob[k]);
    });

    self.total_price = ko.computed(function() {
        return (self.selected_part() && self.selected_part().price) ? self.quantity() * self.selected_part().price() : 0.00;
    });

    self.returnFields = function() {
        return fields;
    };

    self._serialize = function() {
        return ko.toJSON({ 'code': self.selected_part().code(), 'quantity': self.quantity() });
    };

    return self;
};

// customvm needs this in window
window.CPARTS = [];
for(var idx in window.PARTS) {
    // turn these object literals into models so they have ufd
    window.CPARTS.push(new PartVM(window.PARTS[idx]));
}

CustomVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "purchase_lines": ko.observableArray,
        "done": ko.observable,
    };

    _.each(fields, function(v, k) {
        self[k] = v(blob[k]);
    });

    self.returnFields = function() {
        return fields;
    };

    self.addLine = function() {
        self.purchase_lines().push(new PartLineVM({'selected_part': {}, 'quantity': 0}));
        self.purchase_lines.valueHasMutated();
        console.log(ko.toJSON(self.purchase_lines()));
    };

    self.removeLine = function(line) { self.purchase_lines.remove(line) };

    self.save = function() {
        alert('{'+$.map(self.purchase_lines(), function(val) { return val._serialize(); }) + '}');
    }

    return self;
};

ClosingVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "done": ko.observable,
    };

    _.each(fields, function(v, k) {
        self[k] = v(blob[k]);
    });

    return self;
};

// initialize a view model from a blob
MasterVM = function(blob) {
    // capture a new copy of UAS into MasterVM's closure
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't one
    blob = blob || {};

    // field types
    var fields = {
        'id': ko.observable,
        'applicant': ApplicantVM,
        'coapplicant': ApplicantVM,
        'billing_address': AddressVM,
        'system_address': AddressVM,
        'pricetable_date': ko.observable,
        'email': ko.observable,
        'approved': ko.observable,
        'package': PackageVM,
        'shipping': ko.observable,
        'monitoring': ko.observable,
        'email': ko.observable,
        'premium': PremiumVM,
        'combo': ComboVM,
        'customize': CustomVM,
        'closing': ClosingVM,
    };

    // try to assign things from blob to fields if they exist
    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        } else {
            ;
        }
    });

    // variables computed from json responses
    // most of these are sugar for their return values
    self.name = ko.computed(function() {
        return self.applicant.fname() + (self.applicant.initial && self.applicant.initial() ? ' ' + self.applicant.initial() + '.' : '') + (self.applicant.lname() ? ' ' + self.applicant.lname() : '');
    });

    self.citystate = ko.computed(function() {
        return self.billing_address.city() + (self.billing_address.state() ? ', ' + self.billing_address.state() : '');
    });

    self.countrysafe = ko.computed(function() {
        return self.billing_address.country() ? self.billing_address.country() : '';
    });

    // computed variables for the nav bar & review section
    self.agreement_id_nav = ko.computed(function() {
        return (self.id && self.id() ? "Agreement ID: " + self.id() : "No Agreement ID");
    });

    self.package_nav = ko.computed(function() {
        if(self.package.selected_package()) {
            return (self.package.selected_package().name) ? "Package: " + self.package.selected_package().name : "No Package";
        } else {
            return "No Package";
        }
    });

    self.monitoring_nav = ko.computed(function() {
        return (self.monitoring()) ? "Monitoring: " + self.monitoring() : "No Monitoring";
    });

    self.shipping_nav = ko.computed(function() {
        return (self.shipping()) ? "Shipping : " + self.shipping() : "No Shipping";
    });

    // XXX: add the rest of the variables that need to be pretty

    // variables included that are not from json (constants)
    self.countries = ["USA"].concat(["Canada"].sort()); // sort everyone else
    self.states = ["AL","AK","AS","AZ","AR","CA","CO","CT","DE","DC","FM","FL","GA","GU","HI","ID","IL","IN","IA","S","KY","LA","ME","MH","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","MP","OH","OK","OR","PW","PA","PR","RI","SC","SD","TN","TX","UT","VT","VI","VA","WA","WV","WI","WY"].concat(["AB","BC","MB","NB","NL","NT","NS","NU","ON","PE","QC","SK","YT"]); // sort states

    // XXX: insert other variables here

    // some ideas for the following functions:
    //  loader functions that make the correct form parts
    //  appear when their preceding form section is complete
    //  helper functions that take form data and construct
    //  other form data

    self.test_cinfo = function() {
        // test completeness and set flag
        if(self.applicant.fname() && self.applicant.lname() && self.billing_address.address() && self.email()) {
            // disable form fields
            $('#cinfo div input, #cinfo div select, #cinfo div button').prop('disabled', true);
            // change label color
            $('#cinfo span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next section, reveal nav, and scroll
            $('#pkgsel, #nav_pkgsel').removeClass('hyde');
            $('body').animate({
                scrollTop: $('#pkgsel').offset().top,
            }, 1000);
        }
    };

    self.clear_cinfo = function() {
        // clear cinfo fields in viewmodel
        self.applicant.fname('');
        self.applicant.initial('');
        self.applicant.lname('');
        self.billing_address.address('');
        self.billing_address.city('');
        self.billing_address.state('');
        self.billing_address.zip('');
        self.billing_address.country('');
        self.email('');
    };

    self.test_pkgsel = function() {
        // test completeness and set flag
        if(self.package.selected_package()) {
            if(self.package.selected_package().code) {
                // disable submit button
                $('#pkgsel div button').prop('disabled', true);
                // change label color
                $('#pkgsel span.tab-pos').removeClass('label-inverse').addClass('label-success');
                // show next section, reveal nav, and scroll
                $('#monitor, #nav_monitor').removeClass('hyde');
                $('body').animate({
                    scrollTop: $("#monitor").offset().top,
                }, 1000);
            }
        }
    };

    self.clear_pkgsel = function() {
        // clear package field in viewmodel
        self.package.selected_package('');
    };

    self.test_monitor = function() {
        // test completeness and set flag
        if(self.monitoring()) {
            // disable submit button
            $('#monitor div button, #monitor div input').prop('disabled', true);
            // change label color
            $('#monitor span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next section, reveal nav, and scroll
            $('#premium, #nav_premium').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#premium").offset().top,
            }, 1000);
        }
    };

    self.clear_monitor = function() {
        // clear monitoring field in viewmodel
        self.monitoring('');
    };

    self.test_premium = function() {
        // test completeness with flag since this is open-ended
        if(self.premium.done()) {
            $('#premium div button, #premium div input').prop('disabled', true);
            // change label color
            $('#premium span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next section, reveal nav, and scroll
            $('#combos, #nav_combos').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#combos").offset().top,
            }, 1000);
        }
    };

    self.clear_premium = function() {
        self.premium.done(false);
        self.premium.selected_codes().removeAll();
        self.premium.contents().removeAll();
    };

    self.test_combo = function() {
        // test completeness with flag since this is open-ended
        if(self.combo.done()) {
            $('#combos div button, #combos div input').prop('disabled', true);
            // change label color
            $('#combos span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next section, reveal nav, and scroll
            $('#custom, #nav_custom').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#custom").offset().top,
            }, 1000);
        }
    };

    self.clear_combo = function() {
        self.combo.done(false);
        self.combo.selected_codes().removeAll();
        self.combo.contents().removeAll();
    };

    self.test_customize = function() {
        // test completeness with flag since this is open-ended
        if(self.customize.done()) {
            $('#custom div button, #custom div input').prop('disabled', true);
            // change label color
            $('#custom span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next 3 sections, reveal navs, and scroll
            $('#services, #nav_services, #promos, #nav_promos, #shipping, #nav_shipping').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#services").offset().top,
            }, 1000);
        }
    };

    self.clear_customize = function() {
        self.customize.done(false);
        self.purchase_lines().removeAll();
    };

    self.test_shipping = function() {
        // test completeness and set flag
        if(self.shipping()) {
            // disable form fields
            $('#shipping div button, #shipping div input').prop('disabled', true);
            // change label color
            $('#shipping span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next section, reveal nav, and scroll
            $('#closing, #nav_closing').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#closing").offset().top,
            }, 1000);
        }
    };

    self.clear_shipping = function() {
        self.shipping('');
    };

    self.test_closing = function() {
        // test completeness with flag since this is open-ended
        if(self.closing.done()) {
            $('#closing div button, #closing div input').prop('disabled', true);
            // change label color
            $('#closing span.tab-pos').removeClass('label-inverse').addClass('label-success');
            // show next 3 sections, reveal navs, and scroll
            $('#review, #nav_review, #publish, #nav_publish, #scroller').removeClass('hyde');
            $('body').animate({
                scrollTop: $("#review").offset().top,
            }, 1000);
        }
    };

    self.clear_closing = function() {
        self.closing.done(false);
    };

    // XXX: insert other fns above this line
    return self;
};

// jquery on ready wrapper to anonymous function
$(function() {

    // create an object that knockout can use to bind
    json_handler = new JSONHandler();
    master_blob = json_handler._load();
    master_settings = new MasterVM(master_blob);

    // apply bindings for knockout
    ko.applyBindings(master_settings);

    // SCROLL SPY

    // scrollspy to activate elements in the navbar when they are visible
    $('body').scrollspy({target: '#navbar', offset: 65});

    // JQUERY DOM MANIPS

    // toggle the info bar
    $('#infobar_resize').click(function(e) {
        $('#infobar_content').toggle();
        $('#infobar').toggleClass("infobar_zero");
        $('#infobar_resize').toggleClass("icon-resize-small icon-resize-full");
    });

    // toggle the info bar resize icon on hover
    $('#infobar_resize').hover(function() {
        $(this).toggleClass("icon-white");
    }, function() {
        $(this).toggleClass("icon-white");
    });

    // JQUERY FORM-SPECIFIC MANIPS

    // customer info
    // select the correct credit button
    var credit_str = "<a class='btn btn-large ";
    if (master_settings.approved()) {
        if (master_settings.approved() == 'approved') { credit_str += "btn-success'><i class='icon-ok icon-white'></i> Approved</a>"; };
        if (master_settings.approved() == 'dcs') { credit_str += "btn-danger'><i class='icon-remove icon-white'></i> Approved DCS</a>"; };
        if (master_settings.approved() == 'no hit') { credit_str += "btn-warning'><i class='icon-warning-sign icon-white'></i> No Hit</a>"; };
        $('#credit_btn').empty().append(credit_str);
    }


    // FORM LOGIC

    // fire all the test functions to see which sections
    // have already been completed as per the input json
    // these test functions should show the next section
    // and perhaps disable form input (need guidance here)
    // if all of their properties are present in the json
    // received from the server
    master_settings.test_cinfo();
    master_settings.test_pkgsel();
    master_settings.test_monitor();
    master_settings.test_premium();
    master_settings.test_combo();
    master_settings.test_customize();
    master_settings.test_shipping();
    master_settings.test_closing();

    // XXX: more form section handlers...

    // customer info
    $('#cinfo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // fire test and save the viewmodel contents
        master_settings.test_cinfo();
        json_handler._save(master_settings);
    });
    $('#cinfo_form').on('reset', function(evt) {
        // knockout does not refresh observables on a reset
        // so old values stay in the viewmodel but the fields
        // are all blank
        master_settings.clear_cinfo();
    });
    
    // package select
    $('#pkgsel_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.package.done(true);
        master_settings.test_pkgsel();
        json_handler._save(master_settings);
    });
    $('#pkgsel_form').on('reset', function(evt) {
        // blank out package selection
        master_settings.clear_pkgsel();
    });

    // monitoring
    $('#monitor_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.test_monitor();
        json_handler._save(master_settings);
    });
    $('#monitor_form').on('reset', function(evt) {
        // blank out monitoring selection
        master_settings.clear_monitor();
    });

    // premium addons
    $('#premium_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.premium.done(true);
        master_settings.test_premium();
        json_handler._save(master_settings);
    });
    $('#premium_form').on('reset', function(evt) {
        // blank out premium items selection
        master_settings.clear_premium();
    });

    // combos
    $('#combo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.combo.done(true);
        master_settings.test_combo();
        json_handler._save(master_settings);
    });
    $('#combo_form').on('reset', function(evt) {
        // blank out combo selection
        master_settings.clear_combo();
    });

    // customize
    $('#customize_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.customize.done(true);
        master_settings.test_customize();
        json_handler._save(master_settings);
    });
    $('#customize_form').on('reset', function(evt) {
        // blank out combo selection
        master_settings.clear_customize();
    });

    // shipping
    $('#shipping_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.test_shipping();
        json_handler._save(master_settings);
    });
    $('#shipping_form').on('reset', function(evt) {
        // blank out combo selection
        master_settings.clear_shipping();
    });

    // closing
    $('#closing_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();
        
        // save contents of viewmodel as json blob and fire test
        master_settings.closing.done(true);
        master_settings.test_closing();
        json_handler._save(master_settings);
    });
    $('#closing_form').on('reset', function(evt) {
        // blank out combo selection
        master_settings.clear_closing();
    });
});