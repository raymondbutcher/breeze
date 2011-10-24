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
            
            // Hovering over the start button.
            $menu.find('li.start').hover(
                function() {
                    $(this).children('a').addClass('ui-state-hover');
                },
                function() {
                    $(this).children('a').removeClass('ui-state-hover');
                }
            );
            
            // Hovering intentionally over the start button.
            $menu.find('li.start').hoverIntent({
                over: function() {
                    /* Show the admin menu. */
                    
                    var $this = $(this);
                    var $menu = $this.parents('.breeze-menu');
                    var $button = $this.children('a');
                    var $submenu = $this.children('ul');
                    
                    $menu.addClass('ui-widget ui-tabs-collapsible');
                    $menu.removeClass('breeze-menu-off');
                    $button.addClass('ui-helper-hidden');
                    $submenu.addClass('ui-helper-clearfix')
                    $submenu.removeClass('ui-helper-hidden');
                },
                out: function() {
                    /* Hide the admin menu. */
                    
                    var $this = $(this);
                    var $menu = $this.parents('.breeze-menu');
                    var $button = $this.children('a');
                    var $submenu = $this.children('ul');
                    
                    $menu.addClass('breeze-menu-off');
                    $menu.removeClass('ui-widget ui-tabs-collapsible');
                    $button.removeClass('ui-helper-hidden');
                    $submenu.removeClass('ui-helper-clearfix')
                    $submenu.addClass('ui-helper-hidden');
                    
                    // Hide any expanded submenus.
                    $submenu.children('ul > li').each(function() {
                        var $this = $(this);
                        var $button = $this.find('a');
                        if ($button.hasClass('ui-state-active')) {
                            $button.removeClass('ui-state-active');
                            $this.addClass('quick-hide');
                            $this.find('ul').stop(true, true).hide();
                        }
                    });
                    
                },
                timeout: 1000
            });
            
            // Hovering over the main menu.
            $menu.find('.breeze-menu-main li').hover(
                function() {
                    /*
                      Show a hover effect and handle the submenus
                      when the hoverIntent plugin is lagging behind.
                    */
                    
                    // Add the simple hover effect to the button.
                    var $this = $(this);
                    $this.children('a').addClass('ui-state-hover');
                    
                    // Hide any expanded submenus that are still open because
                    // of the hoverIntent event handling.
                    $this.siblings('li').each(function() {
                        var $this = $(this);
                        if ($this.find('ul').length) {
                            var $button = $this.find('a');
                            if ($button.hasClass('ui-state-active')) {
                                $button.removeClass('ui-state-active');
                                $this.addClass('quick-hide');
                                $this.find('ul').stop(true, true).slideUp(50);
                            }
                        }
                    });
                    
                    // Expand this submenu if this function was used to hide
                    // it when a different menu item was hovered. This is
                    // working around hoverIntent's delay.
                    if ($this.hasClass('quick-hide')) {
                        $this.find('a').addClass('ui-state-active');
                        $this.find('ul').stop(true, true).slideDown(75);
                    }
                    
                },
                function() {
                    /*
                      Simply remove the button hover effect. HoverIntent will
                      handle the closing of any remaining expanded submenus.
                    */
                    var $this = $(this);
                    $this.children('a').removeClass('ui-state-hover');
                }
            );
            
            // Hovering intentionally over the main menu.
            $menu.find('.breeze-menu-main li').hoverIntent({
                over: function() {
                    /* Expand the submenu, if it has one. */
                    var $this = $(this);
                    var $ul = $this.find('ul');
                    if ($ul.length) {
                        $this.find('a').addClass('ui-state-active');
                        $this.find('ul').stop(true, true).slideDown(75);
                    }
                },
                out: function() {
                    /* Collapse the submenu, if it has one. */
                    var $this = $(this);
                    var $ul = $this.find('ul');
                    if ($ul.length) {
                        var $button = $this.find('a');
                        if ($button.hasClass('ui-state-active')) {
                            $button.removeClass('ui-state-active');
                            $this.find('ul').stop(true, true).slideUp(50);
                        }
                        $this.removeClass('quick-hide');
                    }
                },
                interval: 10,
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
    */
    
})