$(function() {
    $(".publication").tooltip({
        effect: 'fade',
        fadeOutSpeed: 100,
        predelay: 100,
        delay: 1500,
        position: "bottom left",
        offset: [-15, -40],

        onBeforeShow: function() {
            $(".publication").not(this.getTrigger()).each(function() {
                $(this).data("tooltip").hide();
            });
        }
    });
});
