!(function() {

    $('*[rel="popover"]').popover()
    $('*[rel="tooltip"]').tooltip()

    $('tr.row-link').each(function() {
        var $row = $(this)
        var click = function() {
            console.log('asdasd')
            window.location = $row.find('a').attr('href')
        }
        $row.bind('click', click)
        $row.find('a').hover(function(){
            $row.unbind('click')
        }, function(){
            $row.bind('click', click)
        })
    })

})()
