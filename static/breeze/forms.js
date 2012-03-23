// Perform field validation automatically via AJAX.
$('form[data-form-key] :input[name]').each(function() {

    var $field = $(this);

    var $fieldGroup = $field.parents('.control-group');
    var formKey = $field.parents('form').attr('data-form-key');
    var validationURL = '/form-validation/' + formKey;

    var timeout;
    var cache = {};

    function showResult() {
        var value = $field.val();
        data = cache['v' + value];
        if (data == undefined) {
            return false;
        }
        $fieldGroup
        .find('.help-inline')
        .remove();
        if (data.success) {
            $fieldGroup
            .removeClass('error')
            .addClass('success');
        }
        if (data.error) {
            $fieldGroup
            .removeClass('success')
            .addClass('error')
            .find('.input-append')
            .after(
                $('<span class="help-inline">' + data.error + '</span>')
            );
        }
        return true;
    }

    function validate() {
        postData = {
            name: $field.attr('name'),
            value: $field.val()
        }
        $.ajax({
            url: validationURL,
            type: 'POST',
            context: postData,
            data: postData,
            success: function(data) {
                cache['v' + this.value] = data;
            },
            complete: function() {
                showResult();
            }
        });
    }

    $field.bind('blur change keyup', function(event) {
        clearTimeout(timeout);
        if (!showResult()) {
            if (event.type == 'keyup') {
                timeout = setTimeout(validate, 1000);
            } else {
                validate();
            }
        }
    });

    //$field.keyup(function() {
    //    clearTimeout(timeout);
    //    timeout = setTimeout(validate, 1000);
    //});

});