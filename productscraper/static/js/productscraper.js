$( function () {

	$('.cat-link').each( function () {
		$(this).click( function () {
			var id = this.id;
			var ul = $('#prod-list');
			var title = $('#prod-list-title');

			ul.hide();
			title.hide();
			ul.empty();

			$('#loader').show();

			$.ajax({
				url: '/product/category/' + id,
			}).done (function (result) {
				title.html("Viewing " + result.length + " products for category ID: " + id);
				$('#loader').hide();

				for (var i in result) {
					// build list elements
					var li = $('<li/>').appendTo(ul);
					var link = $('<a/>')
						.text(result[i].prodName + " (" + result[i].prodCode + ")")
						.attr('href', result[i].prodUrl)
						.attr('target', '_blank')
						.appendTo(li);
					var img = $('<img/>')
						.attr('src', result[i].prodImg)
						.attr('height', 100)
						.prependTo(link)
				}
				ul.show();
				title.show();
			});
		});
	});
});
