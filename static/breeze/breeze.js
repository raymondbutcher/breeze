$(document).ready(function() {
    
    
    
    
    
    // Define the menu structure.
    var menu_structure = [
        {
            title: 'Edit',
            icon: 'ui-icon-pencil',
            options: [
                {title: '?????', icon: 'help'},
            ]
        },
        {
            title: 'Articles',
            icon: 'ui-icon-document',
            options: [
                {title: 'Create Article', icons: {primary: 'ui-icon-document'}},
                {title: 'Find Article', icons: {primary: 'ui-icon-search'}}
            ]
        },
        {
            title: 'Feeds',
            icon: 'ui-icon-signal-diag',
            options: [
                {title: 'Create Feed', icons: {primary: 'ui-icon-signal-diag'}},
                {title: 'Find Feed', icons: {primary: 'ui-icon-search'}}
            ]
        },
        {
            title: 'Users',
            icon: 'ui-icon-person',
            options: [
                {title: 'Create User', icons: {primary: 'ui-icon-person'}},
                {title: 'Create Group', icons: {primary: 'ui-icon-key'}},
                {title: 'Find User', icons: {primary: 'ui-icon-search'}},
                {title: 'Find Group', icons: {primary: 'ui-icon-search'}},
            ]
        },
    ]
    
    // Create the menu elements.
    var $menu = $('<div id="breeze-admin"><ul></ul></div');
    var $tabs = $menu.find('ul');
    
    // Turn the menu structure into HTML elements.
    $(menu_structure).each(function(index) {
        var menu_id = 'breeze-admin-' + index;
        var $tab = $('<li><a href="#' + menu_id + '"><span>' + this.title + '</span></a></li>');
        if (this.icon) {
            $tab.find('a').prepend($('<span class="ui-icon ' + this.icon + '"></span>'));
        }
        var $content = $('<div id="' + menu_id + '"><ul class="ui-helper-clearfix"></ul></div>');
        $(this.options).each(function(index) {
            var option_id = menu_id + '-' + index;
            var $item = $('<li></li>');
            $item.append($('<input type="radio" id="' + option_id + '" name="' + menu_id + '-options" />'));
            $item.append($('<label for="' + option_id + '">' + this.title + '</label>'));
            $item.find('#' + option_id).button({
                icons: this.icons
            });
            $content.find('ul').append($item);
        });
        $tabs.append($tab);
        $menu.append($content);
    });
    
    // Turn the menu into a ui-tabs widget.
    $menu.tabs({
        collapsible: true,
        selected: -1
    });
    
    // Add the menu to the top of the page.
    $('body').prepend($menu);
    
    
    
    
    
    //$.ajax({
    //    error: function(jqXHR, textStatus, errorThrown) {
    //        alert('Error during fetch of Breeze menu.\n' + errorThrown);
    //    },
    //    success: function(data, textStatus, jqXHR) {
    //        var $menu = $(data)
    //        $menu.tabs({
    //            collapsible: true,
    //            selected: -1
    //        });
    //        $menu.find('.button').button()
    //        $('body').prepend($menu);
    //    },
    //    url: '/admin/?menu=1'
    //});
    
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