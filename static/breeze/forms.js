// Perform field validation automatically via AJAX.
$('form[data-form-key] .control-group:not([data-no-validation]) :input[name]').each(function() {

    var $field = $(this)
    var $group = $field.parents('.control-group')
    var fieldName = $field.attr('name')
    var multiValue = new Boolean(fieldName.match(/\[\]$/))
    var formkey = $field.parents('form').attr('data-form-key')
    var url = '/form-validation/' + formkey
    var timeout
    var cache = {}

    function getFieldValue() {
        if (multiValue) {
            var result = {},
                values = $field
                        .parent()
                        .find('[name="' + fieldName + '"]')
                        .map(function(){
                            return $(this).val() || ''
                        })
                        .get()
            for (i=0; i<values.length; i++) {
                result[i] = values[i]
            }
            return result
        } else {
            return $field.val()
        }
    }

    function showResult() {
        /* Display the result of the field validation. */
        var data = cache['v' + getFieldValue()] || {}
        if (data.error) {
            $group
                .removeClass('success')
                .addClass('error')
            $tooltip
                .tooltip({
                    animation: true,
                    placement: 'right',
                    trigger: 'manual'
                })
                .attr('data-original-title', data.error)
                .tooltip('show')
            $tooltip
                .data('tooltip')
                .options
                .animation = false;
            return true
        } else if (data.success) {
            $group
                .removeClass('error')
                .addClass('success')
            if ($tooltip.data('tooltip')) $tooltip.tooltip('hide')
            return true
        } else {
            return false
        }
    }

    function validateField() {
        /* Make an AJAX request for this field and show the result. */
        var postData = {
            name: fieldName,
            value: getFieldValue()
        }
        if (multiValue) {
            postData.values = postData.value.length
        }
        console.log(postData);
        $.ajax({
            url: url,
            type: 'POST',
            context: postData,
            data: postData,
            success: function(data) {
                cache['v' + this.value] = data
            },
            complete: function() {
                showResult()
            }
        })
    }

    // Get the element to which the tooltip will be attached.
    var $tooltip = $group
        .find('.controls')
        .find('.help-inline')
        .each(function() {
            // Move server-side errors out of the DOM and into a tooltip.
            var $this = $(this)
            cache['v' + getFieldValue()] = {
                success: false,
                error: $this.text()
            }
            $this.remove()
        })
        .end()
        .children()
        .not('p.help-block')
        .last()

    // If there was a server-side error, then display it.
    showResult()

    $field.bind('blur change keyup', function(event) {
        /* Perform validation immediately for previously validated values,
           or make an AJAX call for new ones. Delay validation for key
           presses so it doesn't make too many requests.
        */
        clearTimeout(timeout)
        if (!showResult()) {
            if (event.type == 'keyup') {
                if (event.keyCode != 9) {
                    // Don't validate when pressing tab,
                    // otherwise it checks an empty field.
                    timeout = setTimeout(validateField, 1000)
                }
            } else {
                validateField()
            }
        }
    })

})
