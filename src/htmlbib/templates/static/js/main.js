$(function() {
    $("ul.tabs").tabs("> .pane");

    $("button.toggler").toggle(
        function () {
            $(this).text("Show details");
            $("section.details", $(this).parent().parent()).hide();
        },
        function () {
            $(this).text("Hide details");
            $("section.details", $(this).parent().parent()).show();
        }
    );
    $("button.toggler").click();
});
