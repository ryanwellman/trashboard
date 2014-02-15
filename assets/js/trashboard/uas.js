
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
            } else if (this[k]._update_from_dict) {
                // recursive viewmodel updates
                this[k]._update_from_dict(v);
            } else {
                this[k] = v
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



    // generic function to ease the next section in
    // args contain jQ compatible names
    // any of these can be blank

    this._next = function(tab, reveal, scroll) {

    };

    // generic function to hide the next and clear buttons
    this._hide = function(form) {
        if(form) {
            $(form + ' .form-actions').addClass('hyde');
        }
    };


    return this;
};
