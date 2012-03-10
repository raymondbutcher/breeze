$deps.ready(['jquery', 'jquery-ui', 'hoverIntent'], function() {
    
    $.ajax({
        url: '/admin/',
        error: function(jqXHR, textStatus, errorThrown) {
            alert('Error during fetch of Breeze menu.\n' + errorThrown);
        },
        success: function(data, textStatus, jqXHR) {
            
            // Insert the menu into the page.
            $menu = $(data);
            $('body').prepend($menu);
            $menu.find('li.start a').show();
            
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
                    
                },
                timeout: 1100 // Must be slightly more than the submenu timeout.
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
                interval: 10, // Use a low interval so it is more responsive.
                timeout: 900 // Must be slightly less than the main menu timeout.
            });
            
        }
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



    







});

$deps.ready('aloha', function() {
    
    var $body = $('body');
    var $document = $(document);
    var hoverLock = false;
    
    $('.container .row .column').each(function() {
        
        var $column = $(this);
        var $otherColumns = $('.container .row .column').not(this);
        
        // Create an edit panel to overlay this column.
        var $editPanel = $('<div class="breeze-edit-panel"></div>');
        
        var editPanelPadding = 10;
        
        var resizeEditPanel = function() {
            var coords = $column.offset();
            
            var borderTop = parseInt($editPanel.css('border-top-width')) || 0,
                borderBottom = parseInt($editPanel.css('border-bottom-width')) || 0,
                borderLeft = parseInt($editPanel.css('border-left-width')) || 0,
                borderRight = parseInt($editPanel.css('border-right-width')) || 0;
            
            var top = Math.max(0, coords.top - editPanelPadding - borderTop);
            var left = Math.max(0, coords.left - editPanelPadding - borderLeft)
            
            var width = $column.outerWidth() + editPanelPadding * 2;
            width = Math.min(width, $document.width() - left - borderLeft - borderRight);
            var height = $column.outerHeight() + editPanelPadding * 2;
            height = Math.min(height, $document.height() - top - borderTop - borderBottom);
            $editPanel.css({
                'top': top,
                'left': left,
                'width': width,
                'height': height
            });
            
            return true;
        }
        $(window).resize(function() {
            resizeEditPanel();
        });
        resizeEditPanel();
        
        $column.data('hoverCount', 0);
        function handleHover(delta) {
            if (hoverLock) {
                return
            }
            var hoverCount = $column.data('hoverCount');
            if (!hoverCount && delta > 0) {
                $otherColumns.stop(true).fadeTo(100, 0.1);
                $otherColumns.data('hoverCount', 0);
                $editPanel.appendTo($body);
            } else if (hoverCount && delta < 0) {
                $otherColumns.stop(true).fadeTo(100, 1);
                $editPanel.detach();
            }
            $column.data('hoverCount', hoverCount + delta);
        }
        
        $.each([$column, $editPanel], function(index, $this) {
            $this.hover(function() {
                handleHover(1);
            }, function() {
                handleHover(-1);
            });
        });
        
        $editPanel.dblclick(function(evt) {
            hoverLock = true;
            setTimeout((function(){
                
                // Remove the edit panel while initializing the Aloha editor.
                $editPanel.detach();
                
                // Make the column editable with Aloha.
                Aloha.jQuery($column.get(0)).aloha();
                
                // Add the edit panel again, with an extra class. Resize it
                // so the new border sizes are taken into account.
                $editPanel.appendTo($body).addClass('breeze-edit-panel-aloha');
                resizeEditPanel();
                
                // Add some event handlers so that the edit panel is resized
                // automatically when the content is changed.
                Aloha.bind('aloha-smart-content-changed', function(jevent, aevent) {
                    resizeEditPanel();
                });
                jQuery(document).keyup(function(event) {
                    resizeEditPanel();
                });
                
                
                var $dialog = $('<div></div>')
                .html('Something something')
                .dialog({
                    //autoOpen: false,
                    buttons: {
                        'OK': function() {
                            $(this).dialog("close");
                        }
                    },
                    //modal: true,
                    position: ['left', 'top']
                    //,
                    //title: 'Basic Dialog'
                });

                
                //GENTICS.Utils.Dom.selectDomNode($column.get(0));
                //Aloha.jQuery($column.get(0)).mahalo();
            }), 5);
        });
        
        
        
    });
});
