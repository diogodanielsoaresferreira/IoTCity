jQuery(document).ready(function($) {

	$(".headroom").headroom({
		"tolerance": 20,
		"offset": 50,
		"classes": {
			"initial": "animated",
			"pinned": "slideDown",
			"unpinned": "slideUp"
		}
	});

});

/* Modal for web images */
$(document).ready(function () {
        $('#myModal').on('show.bs.modal', function (e) {
            var image = $(e.relatedTarget).attr('src');
            $(".img-responsive").attr("src", image);
        });
});

/* Modal for app images */
$(document).ready(function () {
        $('#myModal2').on('show.bs.modal', function (e) {
            var image = $(e.relatedTarget).attr('src');
            $(".img-responsiveapp").attr("src", image);
        });
});

/* Modal for app images */
$(document).ready(function () {
        $('#myModal3').on('show.bs.modal', function (e) {
            var image = $(e.relatedTarget).attr('src');
            $(".img-responsiveapp2").attr("src", image);
        });
});

/* Get description for image in modal */
$(function () {
    $('.pop').on('click', function () {
        var desc = $(this).data('desc');
		var title = $(this).data('title');
		$('.title').text(title);
        $('.desc').text(desc);
    });
});

/* Right sidebar */
$("#sidebar").affix({
    offset: {
      top: 60, bottom: function () {
         return (this.bottom = $('.top-space').outerHeight(true))
		}
    }
});