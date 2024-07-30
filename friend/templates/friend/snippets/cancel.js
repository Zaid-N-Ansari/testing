$(document).ready(function() {
	$("button#cancel-request-btn").on("click", function() {
		const friend = $(this).parent().parent().children().eq(0).text().trim();
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"friend": friend
		}
        $.post("{% url 'friend:cancel' %}", req, function({result, message}) {
            if (result === "success") {
                window.location.reload(true);
            } else {
                alert("Error: " + result);
            }
        }).fail(function(xhr, status, error) {
			console.error(error);
        });
	});
});