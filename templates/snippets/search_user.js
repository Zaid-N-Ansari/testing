$(document).ready(function () {
	let currentPage = 1;  // Initialize current page
	const itemsPerPage = 2;  // Number of items per page

	$("input#user_search").parent().children().children().on("click", function () {
		if ($("input#user_search").val() !== "") {
			$("div#search_result").parent()[0].classList.remove("d-none");
			searchUsers(currentPage); // Call searchUsers with the current page
		} else {
			$("div#search_result").empty();
			$("#pagination_controls").empty(); // Clear pagination controls
			$("div#search_result").parent()[0].classList.add("d-flex");
		}
	});

	$("input#user_search").on("keydown click keyup", function (e) {
		if (e.type === "keydown") {
			if (e.code === "Enter" || e.code === "NumpadEnter") {
				e.preventDefault();
				$(this).parent().children().children().click();
			}
		} else if (e.type === "click") {
			$(this).select();
		} else if (e.type === "keyup") {
			if ($(this).val() === "") {
				$("div#search_result").empty();
				$("#pagination_controls").empty(); // Clear pagination controls
			}
		}
	});

	// Function to send AJAX request with pagination
	function searchUsers(page) {
		const userInput = $("input#user_search").val();
		const req = {
			csrfmiddlewaretoken: "{{ csrf_token }}",
			user: userInput,
			page: page, // Include the current page in the request
			items_per_page: itemsPerPage // Include items per page in the request
		};

		$.post("{% url 'account:search' %}", req, function (res) {
			showSearchResult(res); // Update search results
			updatePaginationUI(res.pagination); // Update pagination controls
		});
	}

	// Function to display search results
	function showSearchResult(res) {
		$("div#search_result").empty().append(`<div class="list-group"></div>`);
		$("div#search_result").css({
			"width": "-webkit-fill-available",
			"background-color": "var(--bs-body-bg)",
		});
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

	// Function to update pagination UI
	function updatePaginationUI(pagination) {
		if (!pagination) {
			$("#pagination_controls").empty(); // Clear pagination if no data
			return;
		}

		const { current_page, total_pages } = pagination;

		console.log(total_pages);

		// Create pagination buttons

		let paginationHTML = `<button ${current_page === 1 ? 'disabled' : ''} class="btn btn-sm d-inline-flex ps-0 border-0" onclick="goToPage(1)"><span class="material-icons">first_page</span></button>`;

		paginationHTML += `<button ${current_page === 1 ? 'disabled' : ''} class="btn btn-sm d-inline-flex border-0" onclick="goToPage(${current_page - 1})"><span class="material-icons">west</span></button>`;

		paginationHTML += ` <span>Page ${current_page} of ${total_pages}</span> `;

		paginationHTML += `<button ${current_page === total_pages ? 'disabled' : ''} class="btn btn-sm d-inline-flex pe-0 border-0" onclick="goToPage(${current_page + 1})"><span class="material-icons">east</span></button>`;

		paginationHTML += `<button ${current_page === total_pages ? 'disabled' : ''} class="btn btn-sm d-inline-flex border-0" onclick="goToPage(${total_pages})"><span class="material-icons">last_page</span></button>`;

		$("#pagination_controls").html(paginationHTML);
	}

	// Function to navigate pages
	window.goToPage = function (page) {
		currentPage = page; // Update the current page
		searchUsers(currentPage); // Fetch new page results
	};
});