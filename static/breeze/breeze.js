$(document).ready(function() {
    
    $.ajax({
        error: function(jqXHR, textStatus, errorThrown) {
            alert('Error during fetch of Breeze menu.\n' + errorThrown);
        },
        success: function(data, textStatus, jqXHR) {
            
            // Insert the menu into the page, fading it in.
            $menu = $(data);
            $('body').prepend($menu);
            $menu.find('li.start a').fadeTo(0, 0).fadeTo('slow', 1);
            
            // Simple hover effect for the start icon.
            $menu.find('li.start').hover(
                function() {
                    $(this).children('a').addClass('ui-state-hover');
                },
                function() {
                    $(this).children('a').removeClass('ui-state-hover');
                }
            );
            
            // Display the main menu when hovering intentionally.
            $menu.find('li.start').hoverIntent({
                over: function() {
                    var $this = $(this);
                    var $menu = $this.parents('.breeze-menu');
                    $menu.addClass('ui-widget ui-tabs-collapsible');
                    $menu.removeClass('breeze-menu-off');
                    var $submenu = $this.children('ul');
                    $submenu.addClass('ui-helper-clearfix')
                    $submenu.removeClass('ui-helper-hidden');
                    var $button = $this.children('a');
                    $button.addClass('ui-helper-hidden');
                },
                out: function() {
                    var $this = $(this);
                    var $menu = $this.parents('.breeze-menu');
                    $menu.addClass('breeze-menu-off');
                    $menu.removeClass('ui-widget ui-tabs-collapsible');
                    var $submenu = $this.children('ul');
                    $submenu.removeClass('ui-helper-clearfix')
                    $submenu.addClass('ui-helper-hidden');
                    var $button = $this.children('a');
                    $button.removeClass('ui-helper-hidden');
                },
                timeout: 500
            });
            
            // Simple hover effect for menu icons, plus hiding submenus
            // immediately when switching between menus.
            $menu.find('.breeze-menu-main li').hover(
                function() {
                    var $this = $(this);
                    $this.children('a').addClass('ui-state-hover');
                    
                    $this.siblings('li').each(function() {
                        var $this = $(this);
                        var $a = $this.find('a');
                        if ($a.hasClass('ui-state-active')) {
                            $a.removeClass('ui-state-active');
                            $this.find('ul').stop(true, false).slideUp(0);
                        }
                    });
                    
                },
                function() {
                    var $this = $(this);
                    $this.children('a').removeClass('ui-state-hover');
                }
            );
            
            // Display the submenu when hovering intentionally.
            $menu.find('.breeze-menu-main li').hoverIntent({
                over: function() {
                    var $this = $(this);
                    var $ul = $this.find('ul');
                    if ($ul.length) {
                        $this.find('a').addClass('ui-state-active');
                        $this.find('ul').stop(true, false).slideDown(75);
                    }
                },
                out: function() {
                    var $this = $(this);
                    var $ul = $this.find('ul');
                    if ($ul.length) {
                        var $a = $this.find('a');
                        if ($a.hasClass('ui-state-active')) {
                            $a.removeClass('ui-state-active');
                            $this.find('ul').stop(true, false).slideUp(50);
                        }
                    }
                },
                timeout: 2000
            });
            
        },
        url: '/admin/?menu=gotime'
    });
    
    /*
    var $dialog = $('<div></div>')
        .html('Something something')
        .dialog({
            autoOpen: false,
            buttons: {
                'OK': function() {
                    $(this).dialog("close");
                }
            },
            //modal: true,
            position: ['left', 'top'],
            title: 'Basic Dialog'
        });
    
    var renderPage = function(data) {
        
        
        $dialog.dialog('open');
        
        
        
        //$('div.page.container').empty();
        //
        //$(data).each(function() {
        //    
        //    var title = this.title
        //    var content = this.content
        //    
        //    
        //    alert(title );
        //});
        
        
    }
    
    
    $.ajax({
        error: function(jqXHR, textStatus, errorThrown) {
            alert('Error during fetch of page templates.\n' + errorThrown);
        },
        success: function(data, textStatus, jqXHR) {
            renderPage(data.pages[0]);
        },
        url: '/static/breeze/page-templates.json'
    });
    */
    
})