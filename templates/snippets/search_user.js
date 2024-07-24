$(document).ready(function () {
	$("input#user_search").parent().children().children().on("click", function () {
		if ($("input#user_search").val() !== "") {
			const req = {
				"csrfmiddlewaretoken": "{{ csrf_token }}",
				"user": $("input#user_search").val()
			}
			$.post("{% url 'account:search' %}", req, function (res) {
				showSearchResult(res);
			});
		}
		else {
			$("div#search_result").empty();
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
			}
		}
	});

	function showSearchResult(res) {
		$("div#search_result").append(`<div class="list-group"></div>`);
		$("div#search_result").css({
			"width": "30dvh",
			"translate": "14dvh 4.5dvh",
			"background-color": "var(--bs-body-bg)",
		});
		$("div#search_result > div.list-group").empty();
		if (res !== null && res.result !== null) {
			Object.entries(res).forEach(([key, user]) => {
				$("div#search_result > div.list-group").append(
					`<a href="/account/profile/${user.username}" class="list-group-item list-group-item-action d-flex flex-row align-items-center justify-content-between" target="_blank">
						${user.username}
						<img src="${user.profile_image}" loading="lazy" style="width: 5dvh;" />
					</a>`
				);
			});
		}
		else {
			$("div#search_result > div.list-group").append(
				`<button class="btn list-group-item list-group-item-action">No User Found</button>`
			);
		}
	}
});