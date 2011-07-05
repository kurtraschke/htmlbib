$(function() {
    $("ul.tabs").tabs("> .pane");
    
    $("button.toggler").toggle(
        function () {
            $(this).text("Show details");
            $(this).next().hide();
        },
        function () {
            $(this).text("Hide details");
            $(this).next().show();
        }
    );
    $("button.toggler").click();
});