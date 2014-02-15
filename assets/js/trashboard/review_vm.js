

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

    self.calculate_monthly_cost = ko.computed(function() {
        // package items

        // monitoring

        // premium items

        // combos

        // alacarte

        // services

        // shipping
    });



    return self;
};

