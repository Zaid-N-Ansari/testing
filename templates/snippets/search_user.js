$(document).ready(function () {
	let currentPage = 1;
	const itemsPerPage = 3;

	$("input#user_search").parent().children().children().on("click", function () {
		if ($("input#user_search").val() !== "") {
			$("ul#search_result").parent().removeClass("d-none");
			searchUsers(currentPage);
		} else {
			$("ul#search_result").empty();
			$("#pagination_controls").empty();
			$("ul#search_result").parent()[0].addClass("d-flex");
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
				$("ul#search_result").empty();
				$("#pagination_controls").empty();
			}
		}
	});

	function searchUsers(page) {
		const userInput = $("input#user_search").val();
		const req = {
			"csrfmiddlewaretoken": "{{ csrf_token }}",
			"user": userInput,
			"page": page,
			"items_per_page": itemsPerPage
		};

		$.post("{% url 'account:search' %}", req, function (res) {
			showSearchResult(res);
			updatePaginationUI(res.pagination);
		});
	}

	function showSearchResult(res) {
		$("ul#search_result").css("width", "-webkit-fill-available");
		$("ul#search_result").empty();
		if (res.result) {
			Object.entries(res.result).forEach(([key, user]) => {
				$("ul#search_result").append(
					`<li class="list-group-item list-group-item-action">
						<a href="/account/profile/${user.username}" class="d-flex flex-row align-items-center justify-content-between" target="_blank">
							${user.username}
							<img src="${user.profile_image}" loading="lazy" class="rounded-circle" style="width: 3rem;" />
						</a>
					</li>`
				);
			});
		} else {
			$("ul#search_result").append(
				`<li class="btn list-group-item list-group-item-action text-center">No User Found</li>`
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

	window.goToPage = function (page) {
		currentPage = page;
		searchUsers(page);
	};
});