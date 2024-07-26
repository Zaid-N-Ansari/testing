$(document).ready(function () {
	let currentPage = 1;
	const itemsPerPage = 2;

	$("input#user_search").parent().children().children().on("click", function () {
		if ($("input#user_search").val() !== "") {
			$("div#search_result").parent().removeClass("d-none");
			searchUsers(currentPage);
		} else {
			$("div#search_result").empty();
			$("#pagination_controls").empty();
			$("div#search_result").parent()[0].addClass("d-flex");
		}
	});

	$("input#user_search").on("keydown click keyup change", function (e) {
		if (e.type === "keydown") {
			if (e.code === "Enter" || e.code === "NumpadEnter") {
				e.preventDefault();
				$(this).parent().children().children().click();
			}
		} else if (e.type === "click") {
			$(this).select();
		} else if (e.type === "keyup" || e.type === "change") {
			if ($(this).val() === "") {
				$("div#search_result").empty();
				$("#pagination_controls").empty();
			}
		}
	});

	function searchUsers(page) {
		const userInput = $("input#user_search").val();
		const req = {
			csrfmiddlewaretoken: "{{ csrf_token }}",
			user: userInput,
			page: page,
			items_per_page: itemsPerPage
		};

		$.post("{% url 'account:search' %}", req, function (res) {
			showSearchResult(res);
			updatePaginationUI(res.pagination);
		});
	}

	function showSearchResult(res) {
		$("div#search_result").empty().append(`<div class="list-group"></div>`);
		$("div#search_result").css("width", "-webkit-fill-available");
		$("div#search_result > div.list-group").empty();
		if (res.result !== null) {
			Object.entries(res.result).forEach(([key, user]) => {
				$("div#search_result > div.list-group").append(
					`<a href="/account/profile/${user.username}" class="list-group-item list-group-item-action d-flex flex-row align-items-center justify-content-between" target="_blank">
                        ${user.username}
                        <img src="${user.profile_image}" loading="lazy" style="width: 5dvh;" />
                    </a>`
				);
			});
		} else {
			$("div#search_result > div.list-group").append(
				`<button class="btn list-group-item list-group-item-action text-center">No User Found</button>`
			);
		}
	}

	function createButton(page, isDisabled, icon, tooltip) {
		return `<button ${isDisabled ? 'disabled' : ''} class="btn btn-sm d-inline-flex border-0" onclick="goToPage(${page})" type="button"><span class="material-icons">${icon}</span></button>`;
	}

	function updatePaginationUI(pagination) {
		if (!pagination) {
			$("#pagination_controls").empty();
			return;
		}
		const { current_page, total_pages } = pagination;

		const paginationHTML =
			`${createButton(1, current_page === 1, 'first_page')}
			${createButton(current_page - 1, current_page === 1, 'west')}
			<span class="mx-2">Page ${current_page} of ${total_pages}</span>
			${createButton(current_page + 1, current_page === total_pages, 'east')}
			${createButton(total_pages, current_page === total_pages, 'last_page')}`;

		$("#pagination_controls").html(paginationHTML);
	}

	// Function to navigate pages
	window.goToPage = function (page) {
		currentPage = page;
		searchUsers(page);
	};
});