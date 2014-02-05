
// fix the window level vars for this to work
_.each(window.PRODUCTS, function(prod) {
    // There is a price in the pricetable for this object so it is purchasable.
    // XXX: This might need to check that the price is not null, but I'm not sure just yet.

    prod.product_price = window.PRICES[prod.code];
    prod.available = !!prod.product_price;

});

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

//window.package_index = _.object(_.pluck(window.PACKAGES, 'code'), window.PACKAGES);
//window.part_index = _.object(_.pluck(window.PARTS, 'code'), window.PARTS);


// capture window.agreement_id from django if it was passed in


// money formatting function
function formatCurrency(value) {
    return Number(value).toFixed(2);
};

// fast hash function
function hashFNV(str) {
    // implementation of the fnv-1a hashing algorithm
    // http://www.isthe.com/chongo/tech/comp/fnv/#FNV-1a

    var hash = 0x811C9DC5; // magic 32 bit fnv offset 2166136261 in hex
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i); // obtain a byte (ASCII char code 0-255)

        // xor hash with char first as in fnv-1a
        hash ^= char;

        // 2^24 + 2^8 + 2^7 + 2^4 + 2 = 13777618 plus the copy on the left of the +=
        // makes the magic 32 bit fnv prime 16777619 you needed to multiply here
        hash += (hash << 24) + (hash << 8) + (hash << 7) + (hash << 4) + (hash << 1);
    }
    return (hash >>> 0); // remove sign from hash
}

// returns a css-formatted hsla color function deterministically generated from
// an input string
function str2hsla(str, alpha) {
    // obtain last 8 bytes of the hash
    var hash = (hashFNV(str) & 0x00000000ffffffff) >>> 0;

    // obtain hsl values
    var h = hash % 360;
    var s = (hash % 25) + 75; // between 75 and 100
    var l = (hash % 30) + 40; // between 40 and 70

    return "hsla(" + h + ", " + s + "%, " + l + "%, " + alpha + ")";
}

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

    // generic function to test a UAS's completeness
    this._test = function(fields) {
        fields = fields || [];

        // return false if fields is blank
        if(!fields) {
            return false;
        }

        // create list of 'is it empty?' values
        var flags = [];
        _.each(fields, function(v, k) {
            // dereference observables for their values
            var cond = (typeof v == 'function') ? v() : v;
            flags.push(!cond);
        });

        // if anything is empty (true), return false
        return !_.reduce(flags, function(memo, v) {
            return memo || v;
        });
    };

    this._clear = function (fields) {
        fields = fields || [];

        // nothing was cleared
        if (!fields) {
            return;
        }

        // go through the fields and clear them
        _.each(fields, function(v, k) {
            if(typeof v == 'function') {
                // feed observables a blank and removeAll on arrays
                if(v() instanceof Array) {
                    v().removeAll();
                } else {
                    v('');
                }
            } else {
                v = '';
            }
        });
    };

    // generic function to lock the section
    this._lock = function(lock) {
        // disable form fields
        $(lock).prop('disabled', true);
    };

    // generic function to ease the next section in
    // args contain jQ compatible names
    // any of these can be blank
    this._next = function(tab, reveal, scroll) {
        // change label color
        if(tab) {
            $(tab + ' span.tab-pos').removeClass('label-inverse').addClass('label-success');
        }
        // reveal actual sections and the nav bars
        if(reveal) {
            $(reveal).removeClass('hyde');
        }
        // animate scroll bar to next section
        if(scroll) {
            $('body').animate({
                scrollTop: $(scroll).offset().top,
            }, 1000);
        }
    };

    // generic function to hide the next and clear buttons
    this._hide = function(form) {
        if(form) {
            $(form + ' .form-actions').addClass('hyde');
        }
    };

    // give everyone the color generator
    this._str2hsla = str2hsla;

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
            url: '/json/' + window.agreement_id,
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
            console.log("loaded json" + (window.agreement_id ? " from agreement " + window.agreement_id : ''));
            console.log(ko.toJSON(data))
        });

        return payload;
    };

    // this fn allegedly saves the contents of obj
    // XXX: needs to be better
    self._save = function(obj) {
        // obtain a payload and declare a return value outside the promise
        payload = ko.toJSON(obj);
        retval = '';

        var result = $.ajax({
            type: "POST",
            dataType: "json",
            url: '/json/' + window.agreement_id,
            async: false, // testing with and without this
            data: payload,
        });

        result.fail(function(xhr, status, error) {
            console.log('failed! (' + error + ') ' + status);
            console.log(xhr.responseText);
        });

        result.done(function(data) {
            // obtain that agreement id from the json response
            console.log(data);
            obj.id = data.id;  // scope spam
            window.agreement_id = data.id;
            retval = data.id;
            console.log("saved json" + (window.agreement_id ? " to agreement " + window.agreement_id :  '') + "\n" + ko.toJSON(self));
        });

        // return the agreement id that was saved
        return retval;
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

    self.complete = function() {
        return self._test([self.fname() && self.lname()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
    };

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

    self.complete = function() {
        // we can figure out what country you're in from the state
        return self._test([self.address(), self.city(), self.state(), self.zip()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
    };

    return self;
};

// this is ryan's vm for packages translated to the new style

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

    // selected_package is another one of those special things that has
    // to come out of one of the window variables
    if(self.selected_package().code) {
        self['selected_package'](package_index[self.selected_package().code]);
    }

    // if there's no customization lines the customize button doesn't work
    // the customization lines need to be updated with quantities as well
    self.prepare_clines = function() {
        // fill the customization lines with available parts
        _.map(window.PRODUCTS_BY_TYPE.Part, function(part) {
            var cline= {
                code: part.code,
                part: part,
                quantity: ko.observable(0),
                min_quantity: ko.observable(0),
            };

            // subscribe this to cust_quantity_changed
            cline.quantity.subscribe(self.cust_quantity_changed);
            self.customization_lines.push(cline);
            cline.quantity.subscribe(self.cust_quantity_changed);
        });

        // now fill them with the correct quantities
        if(self.updated_contents().length && self.changed_contents()) {
            // did we pass in an updated package from the backend?
            _.each(self.updated_contents(), function(line) {
                // Find the customization line for that product
                var cline = _.find(self.customization_lines(), function(cline) {
                    return cline.code == line.code;
                });
                // Set that customization line's quantity and min quantity appropriately.
                if(cline) {
                    //console.log("Found matching cline, ", cline.quantity);
                    cline.quantity(line.quantity);
                    //TODO: Set min quantity
                } else {
                    //console.log("!Found matching cline", cline);
                }
            });
        } else if(self.selected_package().contents && self.selected_package().contents.length && !self.changed_contents()) {
            // deal with the regular package contents instead if not
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

    self.select_package = function(package) {
        if(self.done()) {
            return;
        }

        self.selected_package(package);
        self.custom_quantities = {};
        self.customization_lines.removeAll();
        // clear out any updated contents when selected package changes
        self.updated_contents([]);
        self.changed_contents(false);
        self.customizing(false);

        if(!self.customization_lines().length) {
            _.map(window.PRODUCTS_BY_TYPE.Part, function(part) {
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
        // this needs to unlock the form when you click it
        self.done(false);
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
        $('body').animate({
            scrollTop: $('#pkgsel').offset().top,
        }, 1000);
    };

    self.cancel_customization = function() {
        self.customizing(false);
        $('body').animate({
            scrollTop: $('#pkgsel').offset().top,
        }, 1000);
    };

    self._serialize = function() {
        ret = {
            'customizations': self.customization_deltas,
            'package': self.selected_package().code,
        };
        return JSON.stringify(ret);
    };

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear([self.selected_package]);
        self.done(false);
    };

    // this has to be at the bottom if a package is selected (saved in)
    self.prepare_clines();

    return self;
};

// create some more indices for these things
window.premium_index = _.object(_.pluck(window.PREMIUM, 'code'), window.PREMIUM);
window.combo_index = _.object(_.pluck(window.COMBOS, 'code'), window.COMBOS);
window.closer_index = _.object(_.pluck(window.CLOSERS, 'code'), window.CLOSERS);

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

    // ko needs the things in selected_codes to be things from window vars
    codes = []
    _.each(self.selected_codes(), function(v, k) {
        codes.push(window.premium_index[v.code]);
    });
    self.selected_codes(codes);

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

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
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

    // ko needs the things in selected_codes to be things from window vars
    codes = []
    _.each(self.selected_codes(), function(v, k) {
        codes.push(window.combo_index[v.code]);
    });
    self.selected_codes(codes);

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

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};

// next two view models are for alacarte
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

// all a-la-carte vms need this in window
window.CPARTS = [];
window.DPARTS = {};
for(var idx in window.PARTS) {
    // turn these object literals into models so they can be manipulated directly
    var temp = new PartVM(window.PARTS[idx]);
    window.CPARTS.push(temp);
    window.DPARTS[temp.code()] = temp; // hash to access things in CPARTS by code...
}

PartLineVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "selected_part": PartVM,
        "quantity": ko.observable,
    };

    // ...since the knockout bindings of each drop-down are the actual PartVMs we created above
    // this vm is also special in that it needs to be able to fill itself from the blob but not
    // with just any old unregulated PartVM; they must be the ones that knockout knows about
    self['quantity'] = fields['quantity'](blob['quantity']);
    self['selected_part'] = window.DPARTS[blob['selected_part']['code']];

    self.total_price = ko.computed(function() {
        // ko.computeds only update when an observable they referenced on their first run (undocumented!)
        // changes; we must use this arcane, twisted way of returning zero
        if(self.selected_part) {
            return (self.selected_part.code() && self.selected_part.price()) ? self.quantity() * self.selected_part.price() : 0.00;
        } else {
            return self.quantity() * 0; // drop-down is empty
        }
    });

    self.returnFields = function() {
        return fields;
    };

    self._serialize = function() {
        return ko.toJSON({ 'code': self.selected_part.code(), 'quantity': self.quantity() });
    };

    return self;
};

ALaCarteVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        "purchase_lines": ko.observableArray, // contains non-observable PartLineVMs
        "done": ko.observable,
    };

    // alacarte vm is kind of special, it needs to be able to fill its internal array from the blob
    self['done'] = fields['done'](blob['done']);
    self['purchase_lines'] = fields['purchase_lines']();
    _.each(blob['purchase_lines'], function(v, k) {
        self.purchase_lines().push(new PartLineVM(v));
        self.purchase_lines.valueHasMutated();
    });

    self.returnFields = function() {
        return fields;
    };

    self.dirtyRefresh = function () {
        // non-observable contents of observable arrays need this to work when valueHasMutated won't
        // http://stackoverflow.com/questions/13231738/refresh-observablearray-when-items-are-not-observables
        var data = self.purchase_lines();
        self.purchase_lines([]);
        self.purchase_lines(data);
    };

    self.addLine = function() {
        self.purchase_lines().push(new PartLineVM({'selected_part': {}, 'quantity': 0}));
        self.purchase_lines.valueHasMutated();
    };

    self.removeLine = function(line) { alert('removing!'); self.purchase_lines.remove(line) };

    self.save = function() {
        alert('{'+$.map(self.purchase_lines(), function(val) { return val._serialize(); }) + '}');
    }

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};


ClosingVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_codes': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // ko needs the things in selected_codes to be things from window vars
    codes = []
    _.each(self.selected_codes(), function(v, k) {
        codes.push(window.closer_index[v.code]);
    });
    self.selected_codes(codes);

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};


PromoVM = function(blob) {
    var self = new UpdatableAndSerializable();
    blob = blob || {};

    var fields = {
        'selected_promos': ko.observableArray,
        'selected_services': ko.observableArray,
        'done': ko.observable,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // XXX: ugly
    self.contains = function(param, type) {
        // type | true: promo, false: service
        if(type) {
            return _.contains(self.selected_promos(), param.code);
        } else {
            return _.contains(self.selected_services(), param.code);
        }
    };

    self.complete = function() {
        return self._test([self.done()]);
    };

    self.clear = function() {
        self._clear(Object.keys(fields));
        self.done(false);
    };

    return self;
};

// contains this agreement's credit response
CreditDecisionVM = function(blob) {
    // capture a new copy of UAS and make this thing
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't
    blob = blob || {};

    // field types
    var fields = {
        'decision': ko.observable,
        'files': ko.observableArray,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // XXX: additional processing unknown?
};

// contains invoice lines
ReviewVM = function(blob) {
    // capture a new copy of UAS and make this thing
    var self = new UpdatableAndSerializable();

    // make blob a thing if it isn't
    blob = blob || {};

    // field types
    var fields = {
        'contents': ko.observableArray,
    };

    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // strip out parent objects and guarantee the existence/parsing of certain properties
    // to make the knockout easier
    _.each(self.contents(), function(iline) {
        if(iline.parent) {
            iline.parent = iline.parent.id;
        }
        iline.indent = 0;
        if(!iline.monthly_total) {
            iline.monthly_total = '';
        }
        if(!iline.monthly_each) {
            iline.monthly_each = '';
        }
        iline.mandatory = (iline.mandatory == 'True') ? true : false;
    });

    self.treeroots = function() {
        // return things with no parent
        return _.filter(self.contents(), function(iline) {
            return (iline.parent == undefined);
        });
    };

    self.populate = function(node) {
        var buf = [node];

        var children = _.where(self.contents(), { "parent": node.id });
        if(children.length > 0) {
            _.each(children, function(iline) {
                iline.indent += 0.5; // XXX: don't know what's causing this to run twice
                buf = buf.concat(self.populate(iline)); // but this to run once
            });
        }

        return buf;
    };

    // returns the invoice lines in such an order that all the children are right under
    // their immediate parent along with their siblings
    self.tree = function() {
        var buf = [];

        _.each(self.treeroots(), function(iline) {
            buf = buf.concat(self.populate(iline));
        });

        return buf;
    };

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
        'floorplan': ko.observable,
        'promo_code': ko.observable,
        'premium': PremiumVM,
        'combo': ComboVM,
        'alacarte': ALaCarteVM,
        'closing': ClosingVM,
        'services_and_promos': PromoVM,
        'review': ReviewVM,
    };

    // try to assign things from blob to fields if they exist
    _.each(fields, function(v, k) {
        if(blob[k] != undefined) {
            self[k] = v(blob[k]);
        }
    });

    // variables computed from json responses
    // most of these are sugar for their return values
    self.name = ko.computed(function() {
        return self.applicant.fname() + (self.applicant.lname() ? ' ' + self.applicant.lname() : '');
    });

    self.citystate = ko.computed(function() {
        return self.billing_address.city() + (self.billing_address.state() ? ', ' + self.billing_address.state() : '');
    });

    self.countrysafe = ko.computed(function() {
        return self.billing_address.country() ? self.billing_address.country() : '';
    });

    // computed variables for the nav bar & review section
    self.agreement_id_nav = ko.computed(function() {
        return (self.id && self.id() ? self.id() : "No Agreement ID");
    });

    self.package_nav = ko.computed(function() {
        if(self.package.selected_package()) {
            return (self.package.selected_package().name) ? self.package.selected_package().name : "No Package";
        } else {
            return "No Package";
        }
    });

    self.monitoring_nav = ko.computed(function() {
        return (self.monitoring()) ? self.monitoring() : "No Monitoring";
    });

    self.shipping_nav = ko.computed(function() {
        return (self.shipping()) ? self.shipping() : "No Shipping";
    });

    self.chargeback_nav = ko.computed(function() {
        return self.package.cb_balance();
    });

    // attempt to figure out what prices to display in the nav
    // XXX: get this out of ReviewVM
    self.monthly_cost = ko.computed(function() {
        // package items

        // monitoring

        // premium items

        // combos

        // alacarte

        // services

        // shipping
    });

    // XXX: add the rest of the variables that need to be pretty

    // variables included that are not from json (constants)
    self.countries = ["USA"].concat(["Canada"].sort()); // sort everyone else
    self.states = ["AL","AK","AS","AZ","AR","CA","CO","CT","DE","DC","FM","FL","GA","GU","HI","ID","IL","IN","IA","S","KY","LA","ME","MH","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","MP","OH","OK","OR","PW","PA","PR","RI","SC","SD","TN","TX","UT","VT","VI","VA","WA","WV","WI","WY"].concat(["AB","BC","MB","NB","NL","NT","NS","NU","ON","PE","QC","SK","YT"]); // sort states
    self.dwellings = ["One Story", "Two Story", "Business"];
    // XXX: insert other variables here

    // test things that don't have their own viewmodel or have many viewmodels for completeness


    // this function will set the selected monitoring value
    self.selected_monitoring = function(monit) {
        self.monitoring(monit.value);
    };

    self.selected_shipping = function(shipp) {
        self.shipping(shipp.value);
    };

    self.moncss = function(param) {
        return param.code == self.monitoring() ? 'currently_chosen' : '';
    };

    self.shipcss = function(param) {
        return param.code == self.shipping() ? 'currently_chosen' : '';
    };

    // initial info section
    self.initial_complete = function() {
        return self._test([self.billing_address.zip(), self.floorplan()]);
    };

    // customer info section
    self.cinfo_complete = function() {
        return self._test([self.applicant.complete(), self.billing_address.complete(), self.email()]);
    };

    // some ideas for the following functions:
    //  loader functions that make the correct form parts
    //  appear when their preceding form section is complete
    //  helper functions that take form data and construct
    //  other form data

    self.test_initialinfo = function() {
        // test completeness and set flag
        if(self.initial_complete()) {
            self._next('#initial_info', '#pkgsel, #nav_pkgsel', '#pkgsel');
        }
    };

    self.clear_initialinfo = function() {
        // clear initial info fields in viewmodel
        self.billing_address.zip('');
        self.floorplan('');
        self.promo_code('');
    };

    self.test_cinfo = function() {
        // test completeness and set flag
        if(self.cinfo_complete()) {
            self._next('#cinfo', '#shipping, #nav_shipping', '#shipping');
        }
    };

    self.clear_cinfo = function() {
        // clear cinfo fields in viewmodel
        self.applicant.clear();
        self.billing_address.clear();
        self.email('');
    };

    self.test_pkgsel = function() {
        // test completeness and set flag
        if(self.package.complete()) {
            self._next('#pkgsel', '#monitor, #nav_monitor', '#monitor');
        }
    };

    self.clear_pkgsel = function() {
        // clear package field in viewmodel
        self.package.clear();
    };

    self.test_monitor = function() {
        // test completeness and set flag
        if(self.monitoring()) {
            self._next('#monitor', '#premium, #nav_premium', '#premium');
        }
    };

    self.clear_monitor = function() {
        // clear monitoring field in viewmodel
        self.monitoring('');
    };

    self.test_premium = function() {
        // test completeness with flag since this is open-ended
        if(self.premium.complete()) {
            self._next('#premium', '#combos, #nav_combos', '#combos');
        }
    };

    self.clear_premium = function() {
        self.premium.clear();
    };

    self.test_combo = function() {
        // test completeness with flag since this is open-ended
        if(self.combo.complete()) {
            self._next('#combos', '#a_la_carte, #nav_a_la_carte', '#a_la_carte');
        }
    };

    self.clear_combo = function() {
        self.combo.clear();
    };

    self.test_alacarte = function() {
        // test completeness with flag since this is open-ended
        if(self.alacarte.complete()) {
            self._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos', '#services');
        }
    };

    self.clear_alacarte = function() {
        self.alacarte.clear();
    };

    self.test_services_and_promos = function() {
        if(self.services_and_promos.done()) {
            self._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo', '#cinfo');
        }
    };

    self.test_shipping = function() {
        // test completeness and set flag
        if(self.shipping()) {
            self._next('#shipping', '#closing, #nav_closing', '#closing');
        }
    };

    self.clear_shipping = function() {
        self.shipping('');
    };

    self.test_closing = function() {
        // test completeness with flag since this is open-ended
        if(self.closing.complete()) {
            self._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller', '#review');
        }
    };

    self.clear_closing = function() {
        self.closing.clear();
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
    $('body').scrollspy({target: '#right_sidebar', offset: 150});

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

    // test all the sections for completeness and move us to the correct spot
    checklist = [master_settings.initial_complete(), master_settings.package.complete(), master_settings.cinfo_complete(), master_settings.monitoring(), master_settings.premium.complete(), master_settings.combo.complete(), master_settings.alacarte.complete(), master_settings.services_and_promos.done(), master_settings.shipping(), master_settings.closing.complete()];
    first_incomplete = _.reduce(checklist, function(memo, value) { return (value) ? memo + 1 : memo; }, 0); // cannot complete a section w/o clicking next on the one above it

    // reveal the sections up to whichever one is behind
    switch(first_incomplete) {
        case 10:
            master_settings._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller');
            master_settings._hide('#closing_form');
        case 9:
            master_settings._next('#shipping', '#closing, #nav_closing');
            master_settings._hide('#shipping_form');
        case 8:
            master_settings._next('#cinfo', '#shipping, #nav_shipping');
            master_settings._hide('#cinfo_form');
        case 7:
            master_settings._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo');
            master_settings._hide('#promo_form');
        case 6:
            master_settings._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos');
            master_settings._hide('#alacarte_form');
        case 5:
            master_settings._next('#combos', '#a_la_carte, #nav_a_la_carte');
            master_settings._hide('#combo_form');
        case 4:
            master_settings._next('#premium', '#combos, #nav_combos');
            master_settings._hide('#premium_form');
        case 3:
            master_settings._next('#monitor', '#premium, #nav_premium');
            master_settings._hide('#monitor_form');
        case 2:
            master_settings._next('#pkgsel', '#monitor, #nav_monitor');
            master_settings._hide('#pkgsel_form');
        case 1:
            master_settings._next('#initial_info', '#pkgsel, #nav_pkgsel');
            master_settings._hide('#initialinfo_form');
        default:
            break;
    }

    // now do the actual animation
    switch(first_incomplete) {
        default:
            break;
        case 1: // initial info
            master_settings._next('#initial_info', '#pkgsel, #nav_pkgsel', '#pkgsel');
            break;
        case 2: // package select
            master_settings._next('#pkgsel', '#monitor, #nav_monitor', '#monitor');
            break;
        case 3: // monitoring
            master_settings._next('#monitor', '#premium, #nav_premium', '#premium');
            break;
        case 4: // premium items
            master_settings._next('#premium', '#combos, #nav_combos', '#combos');
            break;
        case 5: // combos
            master_settings._next('#combos', '#a_la_carte, #nav_a_la_carte', '#a_la_carte');
            break;
        case 6: // a la carte
            master_settings._next('#a_la_carte', '#services, #nav_services, #promos, #nav_promos', '#services');
            break;
        case 7: // services and promos
            master_settings._next('#services span.tab-pos, #promos', '#cinfo, #nav_cinfo', '#cinfo');
            break;
        case 8: // customer info
            master_settings._next('#cinfo', '#shipping, #nav_shipping', '#shipping');
            break;
        case 9: // shipping
            master_settings._next('#shipping', '#closing, #nav_closing', '#closing');
            break;
        case 10: // closing
            master_settings._next('#closing', '#review, #nav_review, #publish, #nav_publish, #scroller', '#review');
            break;
    }

    // form section button handlers

    // initial info
    $('#initialinfo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // fire test and save the viewmodel contents
        master_settings.test_initialinfo();
        json_handler._save(master_settings);

        // hide the buttons
        master_settings._hide('#initialinfo_form');

        // at this point an agreement id has been assigned, so obtain it
        // XXX: get the entire thing loaded into master_settings
        //      using the _update_from_dict() in UAS
        //blob = json_handler._load(master_settings);
        //master_settings._update_from_dict(blob); // doesn't actually work for some reason
    });
    $('#initialinfo_form').on('reset', function(evt) {
        // knockout does not refresh observables on a reset
        // so old values stay in the viewmodel but the fields
        // are all blank
        master_settings.clear_initialinfo();
    });

    // customer info
    $('#cinfo_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // fire test and save the viewmodel contents
        master_settings.test_cinfo();
        json_handler._save(master_settings);

        // hide the buttons
        master_settings._hide('#cinfo_form');
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

        // hide the buttons
        master_settings._hide('#pkgsel_form');
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

        // hide the buttons
        master_settings._hide('#monitor_form');
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

        // hide the buttons
        master_settings._hide('#premium_form');
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

        // hide the buttons
        master_settings._hide('#combo_form');
    });
    $('#combo_form').on('reset', function(evt) {
        // blank out combo selection
        master_settings.clear_combo();
    });

    // alacarte
    $('#alacarte_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        master_settings.alacarte.done(true);
        master_settings.test_alacarte();
        json_handler._save(master_settings);

        // hide the buttons
        master_settings._hide('#alacarte_form');
    });

    $('#alacarte_form').on('reset', function(evt) {
        // blank out alacarte selection
        master_settings.clear_alacarte();
    });

    // promo and services
    $('#promo_form').on('submit', function(evt) {
        evt.preventDefault();

        master_settings.services_and_promos.done(true);
        master_settings.test_services_and_promos();

        // hide the buttons
        master_settings._hide('#promo_form');
    });

    // shipping
    $('#shipping_form').on('submit', function(evt) {
        // prevent default event
        evt.preventDefault();

        // save contents of viewmodel as json blob and fire test
        master_settings.test_shipping();
        json_handler._save(master_settings);

        // hide the buttons
        master_settings._hide('#shipping_form');
    });
    $('#shipping_form').on('reset', function(evt) {
        // blank out shipping selection
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

        // hide the buttons
        master_settings._hide('#closing_form');
    });
    $('#closing_form').on('reset', function(evt) {
        // blank out closing selection
        master_settings.clear_closing();
    });
    $('#global_save_btn').on('click', function(evt) {
        // just save without checking anything
        json_handler._save(master_settings);
    });
});
