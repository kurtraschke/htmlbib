$(function() {
    $(".publication").tooltip({
        effect: 'fade',
        fadeOutSpeed: 100,
        predelay: 100,
        delay: 1500,
        position: "center left",
        offset: [0, -40],

        onBeforeShow: function() {
            $(".publication").not(this.getTrigger()).each(function() {
                $(this).data("tooltip").hide();
            });
        }
    });
});
