$(document).ready(function () {
	function checkAndChangeTheme(theme) {
		if (theme === "dark") {
			$("header").addClass("bg-dark");
			$("header").removeClass("bg-white");
			$("span.badge").addClass("bg-dark");
			$("span.badge").removeClass("bg-white");
			$("button.switch-theme").children(0).eq(0).text("Dark");
			$("button.switch-theme").children(0).eq(1).text("dark_mode");
		}
		else {
			$("header").addClass("bg-white");
			$("header").removeClass("bg-dark");
			$("span.badge").addClass("bg-white");
			$("span.badge").removeClass("bg-dark");
			$("button.switch-theme").children(0).eq(0).text("Light");
			$("button.switch-theme").children(0).eq(1).text("light_mode");
		}
	}

	function setInitialTheme() {
		const storedTheme = localStorage.getItem("theme");
		if (storedTheme) {
			$("html").attr("data-bs-theme", storedTheme);
			checkAndChangeTheme(storedTheme);
		}
		else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
			$("html").attr("data-bs-theme", "dark");
		} else {
			$("html").attr("data-bs-theme", "light");
		}
	}

	function listenForThemeChanges() {
		const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");

		mediaQueryList.addEventListener("change", (event) => {
			const newColorScheme = event.matches ? "dark" : "light";
			$("html").attr("data-bs-theme", newColorScheme);
			localStorage.setItem("theme", newColorScheme);
			checkAndChangeTheme(newColorScheme);
		});
	}

	$("button.switch-theme").on("click", function (event) {
		const currentTheme = $("html")[0].getAttribute("data-bs-theme");
		const newTheme = currentTheme === "dark" ? "light" : "dark";
		checkAndChangeTheme(newTheme);
		$("html").attr("data-bs-theme", newTheme);
		localStorage.setItem("theme", newTheme);
		$("body").css("transition", "background-color 200ms ease");
		$("header").css("transition", "background-color 200ms ease");
		$("span.badge").css("transition", "background-color 200ms ease");
		$("button.switch-theme").css("transition", "color 200ms ease");
	});

	setInitialTheme();
	listenForThemeChanges();
});