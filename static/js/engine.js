$(document).ready(function() {
    $('.ui.dropdown').dropdown();
    $('#graph-render').html(Viz($('#graph-source').val()));
    $('#graph-source').on('input', function(e) {
        $('#graph-render').html(Viz($('#graph-source').val()));
    });
});
