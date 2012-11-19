!(function() {

    // Initialize popovers and tooltips.
    $('*[rel="popover"]').popover()
    $('*[rel="tooltip"]').tooltip()

    // Make table cells clickable.
    $('table tr').each(function() {
        var $row = $(this)
        var hasAction = false;
        $row.find('td').each(function() {

            var $cell = $(this)

            var $checkbox = $cell.find(':checkbox')
            if ($checkbox.length) {

                var click = function() {
                    $checkbox.prop('checked', !$checkbox.prop('checked'))
                }
                $cell.bind('click', click)
                $checkbox.hover(function(){
                    $cell.unbind('click')
                }, function(){
                    $cell.bind('click', click)
                })

                hasAction = true

            } else {
                var $link = $(this).find('a')
                if (!$link.length) {
                    $link = $row.find('a')
                }
                if ($link.length) {

                    var click = function() {
                        window.location = $link.attr('href')
                    }
                    $cell.bind('click', click)
                    $link.hover(function(){
                        $cell.unbind('click')
                    }, function(){
                        $cell.bind('click', click)
                    })

                    hasAction = true

                }
            }

        })

        if (hasAction) {
            $row.addClass('row-link')
        }

    })

    // Make the table header checkbox affect the other checkboxes.
    $('table thead :checkbox').click(function() {
        var checked = this.checked
        $(this).parents('table').find('tbody :checkbox').each(function() {
            this.checked = checked
        })
    })

    // Handle go-back links.
    $('body').on('click', 'a.go-back', function(event) {
        history.back()
        event.preventDefault()
    })

})()
