$(document).ready(function () {
	$("input#user_search").parent().children().children().on("click", function () {
		const dat = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"user": $("input#user_search").val()
		}
		$.post("{% url 'account:search' %}", dat, function (data) {
			console.log(data===null);
			if(data!==null || data.result !==null)
			$("div#search_result").empty();

		});
	});
});