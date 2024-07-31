$(document).ready(function () {
	const req = {
		"user": "{{ request.user.username }}"
	};
	$.get("{% url 'friend:notifications' %}", req, function (data) {
		const { result } = data;
		if (result.length > 0) {
			$("span#red-dot").addClass("d-block");
			result.forEach(function (notification) {
				const { to_user, created_at } = notification;
				$("div#notifications > ul").append(`
					<li>
						<a target="_blank" class="dropdown-item px-2 text-end" href="#">
							<span>You sent a friend request to ${to_user}</span>
							<span class="small float-end mb-1">${created_at}</span>
						</a>
					</li>
				`);
			});
		}
		else {
			$("span#red-dot").addClass("d-none");
			$("div#notifications > ul").addClass("px-1 text-center");
			$("div#notifications > ul").append(`
				<li>
					<span>No Notifications Yet</span>
				</li>
			`);
		}
	}).fail(function (xhr, status, error) {
		$("span#red-dot").addClass("d-none");
		$("div#notifications > ul").addClass("d-none");
		console.error("Error fetching notifications:", error);
	});
});