$(document).ready(function() {
	$("button#unfriend-btn").on("click", function() {
		const friend = $(this).attr("data-bs-original-title").replace("Unfriend", "").trim();
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"friend": friend
		}
        $.post("{% url 'friend:unfriend' %}", req, function({result, message}) {
            if (result === "success") {
                window.location.reload(true);
            } else {
                alert("Error: " + message);
            }
        }).fail(function(xhr, status, error) {
			console.error(error);
        });
	});
});