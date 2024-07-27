$(document).ready(function() {
	$("button#addfriend-btn").on("click", function() {
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"user": "{{ user }}"
		};
		$.post("{% url 'friend:addfriend' user %}", req, function({result}) {
			(result === "success")?location.reload(true):console.log(result);
		});
	});
	$("button#unfriend-btn").on("click", function() {
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"user": "{{ user }}"
		};
		$.post("{% url 'friend:unfriend' user %}", req, function({result}) {
			(result === "success")?location.reload(true):console.log(result);
		});
	});
});