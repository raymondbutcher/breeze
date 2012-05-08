!(function() {

    var totalColumns = 12

    function renderPageContent($modal, $input) {

        var $table = $modal.find('table')
        var $tbody = $table.find('tbody')
        $tbody.children().remove()

        try {
            var pageContent = $.parseJSON($input.val()) || []
        } catch (error) {
            alert('Error reading page content:' + error)
            var pageContent = []
        }
        if (!pageContent['push']) {
            alert('Error reading page content:' + pageContent)
            pageContent = []
        }
        if (!pageContent.length) {
            pageContent = [{'colspan': 12, 'content': ''}]
        }

        var $undoButton = $modal.find('.undo-button')

        $(pageContent).each(function(rowIndex, row) {

            // Ensure we use up the full amount of columns in each row.
            // If it's short, make a blank column to complete the row.
            var rowColumns = 0
            $(row).each(function() {
                var colspan = parseInt(this.colspan)
                if (isNaN(colspan)) {
                    rowColumns += 1
                } else {
                    rowColumns += colspan
                }
            })
            if (rowColumns < totalColumns) {
                row.push({
                    'colspan': totalColumns - rowColumns,
                    'content': ''
                })
            }

            var $newRow = $('<tr></tr>').appendTo($tbody)

            $(row).each(function(columnIndex, column) {

                $newColumn = $('<td></td>').appendTo($newRow)

                var colspan = parseInt(column.colspan)
                if (isNaN(colspan)) {
                    colspan = 1
                }

                $newColumn.attr('colspan', colspan)
                $newColumn.attr('width', parseInt(100 * colspan / totalColumns) + '%')

                var $container = $('<div class="textarea-container"></div>').appendTo($newColumn)

                var $grabberLeft = $('<div class="grabber grabber-left"></div>').appendTo($container)
                var $textarea = $('<textarea></textarea>').appendTo($container)
                var $grabberRight = $('<div class="grabber grabber-right"></div>').appendTo($container)

                var content = (column.content || '')
                $textarea.val(content)
                $textarea.attr('data-original-value', content)

                $textarea.autosize()

                $textarea.change(function() {
                    var $this = $(this)
                    if ($this.val() == $this.attr('data-original-value')) {
                        $this.parents('td').removeClass('changed')
                        if ($this.parents('table').find('.changed').length == 0) {
                            $undoButton.hide()
                        }
                    } else {
                        $this.parents('td').addClass('changed')
                        $undoButton.show()
                    }
                })

                $textarea.focus(function() {
                    $(this).parents('td').addClass('focus')
                })

                $textarea.blur(function() {
                    $(this).parents('td').removeClass('focus')
                })

                $newColumn.click(function() {
                    $(this).find('textarea').focus()
                })

                var $buttonContainer = $('<p></p>').appendTo($newColumn)
                //var $buttonUndo = $('<a href="#" class="btn">Undo Changes</a>').appendTo($buttonContainer)
                //var $buttonResize = $('<a href="#" class="btn">Delete</a></p>').appendTo($buttonContainer)

            })

        })

        $modal.attr('data-rendered-page-content', 'true')

    }

    $(':input[data-edit-page-content]').each(function() {

        var $input = $(this)
        var $modal = $('#' + $input.attr('data-edit-page-content'))

        var originalValue = $input.val()

        var $undoButton = $modal.find('.undo-button')
        $undoButton.click(function() {
            $input.val(originalValue)
            renderPageContent($modal, $input)
            $undoButton.hide()
        })

        $modal.on('show', function() {
            if (!$modal.attr('data-rendered-page-content')) {
                renderPageContent($modal, $input)
            }
        })

        $modal.on('hide', function(event) {
            var structure = []
            $(this).find('table tbody tr').each(function() {
                var row = []
                $(this).find('td').each(function() {
                    var $column = $(this)
                    row.push({
                        'colspan': $column.attr('colspan'),
                        'content': $column.find('textarea').val()
                    })
                })
                structure.push(row)
            })
            $input.val($.toJSON(structure))
        })

    })

})()
