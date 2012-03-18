(function() {

    $('*[rel="popover"]').popover();

    /*
    $('.navbar .nav a[data-toggle!="modal"]').each(function() {
        var $link = $(this);
        var hash = this.href.match(/#.+$/);
        if (hash) {
            var $target = $(hash[0]);
            var undoTimeout;
            $link.click(function(){
                console.log('clicked');
                $('.targetted').removeClass('targetted');
                $target.addClass('targetted');
                console.log('added class');
                clearTimeout(undoTimeout);
                undoTimeout = setTimeout((function(){
                    $target.removeClass('targetted');
                }), 2000);
            });
        }
    });
    */

})();
