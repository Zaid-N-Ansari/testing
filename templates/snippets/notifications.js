$(document).ready(function () {
	let currentPage = 1;
	const perPage = 2;
	let fetching = false;

	function displayNotifications(data) {
		const { result } = data;

		if (result.length > 0) {
			$("span#red-dot").addClass("d-block").text(result[0].count);

			result.forEach(notification => {
				const { from_user, created_at, action } = notification;
				$("div#notifications > ul").append(`
                    <li>
                        <a target="_blank" class="dropdown-item px-2 text-end" href="/account/profile/${from_user}">
                            <span class="text-end">${action}</span>
                            <span class="small float-end mb-1">${created_at}</span>
                        </a>
                    </li>
                `);
			});
		} else {
			$("span#red-dot").addClass("d-none");
			$("div#notifications > ul").addClass("px-1 text-center").html(`
                <li>
                    <span>No Notifications Yet</span>
                </li>
            `);
		}
	}

	function fetchNotifications(page) {
		if (fetching) return;
		fetching = true;

		const req = {
			user: "{{ request.user.username }}",
			"page": page,
			per_page: perPage
		};

		$.get("{% url 'friend:notifications' %}", req)
			.done(data => {
				displayNotifications(data);
				updateScrollListener(data.pagination);
			})
			.fail((xhr, status, error) => {
				console.error("Error fetching notifications:", error);
			})
			.always(() => {
				fetching = false;
			});
	}

	function updateScrollListener({ current_page, total_pages }) {
		if (current_page < total_pages) {
			$("div#notifications > ul").on("scroll", handleScroll);
		} else {
			$("div#notifications > ul").off("scroll");
		}
	}

	function handleScroll() {
		const $this = $(this);
		const scrollPosition = $this.scrollTop() + $this.height();
		const scrollThreshold = $this[0].scrollHeight - 20;

		if (scrollPosition >= scrollThreshold) {
			currentPage++;
			fetchNotifications(currentPage);
		}
	}
	fetchNotifications(currentPage);
});
