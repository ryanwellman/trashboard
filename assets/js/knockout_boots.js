ko.bindingHandlers.popover = {
    init: function(element, valueAccessor){
        var local = ko.utils.unwrapObservable(valueAccessor()),
            options = {},
            $elem = $(element),
            popoverEvent = 'click',
            popoverAction = 'show';

        ko.utils.extend(options, ko.bindingHandlers.popover.options);
        ko.utils.extend(options, local);

        if (options.trigger === 'hover') {
            popoverEvent = 'mouseenter mouseleave';
        } else if (options.trigger === 'focus') {
            popoverEvent = 'focus blur';
        }

        if(options.trigger !== 'click'){
            popoverAction = 'toggle';
        }

        $elem.on(popoverEvent, function(evt){
            $elem.popover(options).popover(popoverAction);
        });

        $(document).on('click', '[data-dismiss="popover"]', function(evt){
            $elem.popover('hide');
        });
    },

    options: {
        animation: true,
        html: true,
        placement: 'right',
        selector: false,
        trigger: 'manual',
        title: '',
        content: '',
        delay: 0,
        container: false
    }
};
