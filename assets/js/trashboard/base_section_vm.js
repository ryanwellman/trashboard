

/* Every VM needs this stuff. */

function BaseSectionVM(master) {
    var self = UpdatableAndSerializable();

    self.master = master;


    /* None of these functions can have implementations, because you can't super.
       These are just stubs that explain what the functions need to test/do. */

    self.is_complete = ko.computed(function() {
        /* Is this section complete?  Used to determine if this function is done.
        */
        return true;
    });

    self.construct_agreement = function(agreement) {
        /* Given an agreement blob, update the fields on this vm.  (This
        should cause the templates to update).     */

    };

    self.update_from_agreement = function(agreement) {
        /* Given an agreement blob, update the agreement blob with data from the fields
           on this vm. */
    };

    self.nav_template_name = function(agreement) {
        return 'default_nav_template';
    }

    self.template_name = function(agreement) {
        return self.name+'_vm';
    }

    self.completed = ko.computed(function() {

    });

    self.mark_tab_completed = function(tab, reveal, scroll) {
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
    }

    return self;
}