/**
 * Django Admin customization for Weapon model
 * Handles showing/hiding trick weapon fields based on is_trick checkbox
 */
'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // Wait for Django's jQuery to be available
    function initWhenReady() {
        if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
            setTimeout(initWhenReady, 100);
            return;
        }

        var $ = django.jQuery;
        var isTrickCheckbox = $('#id_is_trick');

        function toggleTrickFields() {
            var isTrick = isTrickCheckbox.is(':checked');

            // Hide/show the entire "Secondary Form" fieldset
            $('fieldset').each(function() {
                var $fieldset = $(this);
                var $header = $fieldset.find('h2');
                if ($header.text().indexOf('Secondary Form') !== -1) {
                    if (isTrick) {
                        $fieldset.show();
                        // Expand the fieldset (remove collapsed class)
                        $fieldset.removeClass('collapsed');
                    } else {
                        $fieldset.hide();
                        // Clear the values when hiding
                        $fieldset.find('input, select').val('');
                    }
                }
            });

            // Toggle 'form' column in all inline tables
            $('th').each(function() {
                var $th = $(this);
                if ($th.text().trim() === 'Form') {
                    var columnIndex = $th.index();
                    var $table = $th.closest('table');

                    if (isTrick) {
                        $th.show();
                        $table.find('tbody tr').each(function() {
                            $(this).find('td').eq(columnIndex).show();
                        });
                    } else {
                        $th.hide();
                        $table.find('tbody tr').each(function() {
                            var $cell = $(this).find('td').eq(columnIndex);
                            $cell.hide();
                            $cell.find('select').val('primary');
                        });
                    }
                }
            });

            // Also use class-based approach for field-form
            if (isTrick) {
                $('.field-form').show();
            } else {
                $('.field-form').hide();
                $('.field-form select').val('primary');
            }
        }

        // Initial toggle on page load
        if (isTrickCheckbox.length) {
            setTimeout(function() {
                toggleTrickFields();
            }, 100);

            isTrickCheckbox.on('change', function() {
                toggleTrickFields();
            });
        }

        // Handle dynamically added inline rows
        $(document).on('DOMNodeInserted', function(e) {
            if ($(e.target).hasClass('dynamic-') || $(e.target).find('.dynamic-').length) {
                setTimeout(function() {
                    toggleTrickFields();
                }, 100);
            }
        });
    }

    initWhenReady();
});