$(document).ready(function() {
	$("button#addfriend-btn").on("click", function() {
		const friend = $(this).attr("data-bs-original-title").replace("Friend", "").trim();
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"friend": friend
		}
        $.post("{% url 'friend:addfriend' %}", req, function({result, message}) {
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