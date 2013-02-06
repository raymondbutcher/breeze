!(function() {

    $('.datepicker').each(function() {

        var $input = $(this),
            options = $input.data('datepicker-options') || {}

        $input.datepicker()

    })

    $('.timepicker').each(function() {

        var $input = $(this),
            options = $input.data('timepicker-options') || {}

        $input.timepicker(options)

    })

})()
