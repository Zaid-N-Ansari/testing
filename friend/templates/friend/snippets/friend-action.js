$(document).ready(function() {
	$("button#fr-action-btn").on("click", function(e) {
		e.preventDefault();
		const friend = $(this).attr("data-bs-original-title").replace("Friend", "").trim();
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"user": "{{user}}"
		}
		let url = "";
		if(e.target.ariaValueText === "accept") {
			url = "{% url 'friend:accept' %}";
		}
		else if(e.target.ariaValueText === "reject") {
			url = "{% url 'friend:reject' %}";
		}		
        $.post(url, req, function({result, message}) {			
			if (result === "success") {
                // window.location.reload(true);
            } else {
                alert("Error: " + result);
            }
        }).fail(function(xhr, status, error) {
			console.error(error);
        });
	});
});