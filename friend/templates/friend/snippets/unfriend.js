$(document).ready(function() {
	$("button#unfriend-btn").on("click", function() {
		const friend = $(this).attr("data-bs-original-title").replace("Unfriend", "").trim();
		req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"friend": friend
		}
        $.post("{% url 'friend:unfriend' %}", req, function({result, message}) {
            if (result === "success") {
                location.reload();
            } else {
                alert("Error: " + message);
            }
        }).fail(function(xhr, status, error) {
			console.log(error);
        });
	});
});