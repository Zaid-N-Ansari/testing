function toggleTheme(event) {
	const currentTheme = document.querySelector("html").getAttribute("data-bs-theme");
	const newTheme = currentTheme === "dark" ? "light" : "dark";
	document.querySelector("html").setAttribute("data-bs-theme", newTheme);
	localStorage.setItem("theme", newTheme);
	checkAndChangeTheme(newTheme);
}

function checkAndChangeTheme(theme) {
	if (theme === "dark") {
		document.querySelector("header").classList.remove("bg-white");
		document.querySelector("header").classList.add("bg-dark");
		document.querySelector("button.switch-theme").children[0].innerText = "dark_mode";
		document.querySelector("button.switch-theme").children[1].innerText = "Dark";
	}
	else {
		document.querySelector("header").classList.remove("bg-dark");
		document.querySelector("header").classList.add("bg-white");
		document.querySelector("button.switch-theme").children[0].innerText = "light_mode";
		document.querySelector("button.switch-theme").children[1].innerText = "Light";
	}
}

function setInitialTheme() {
	const storedTheme = localStorage.getItem("theme");
	if (storedTheme) {
		document.querySelector("html").setAttribute("data-bs-theme", storedTheme);
		checkAndChangeTheme(storedTheme);
	}
	else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
		document.querySelector("html").setAttribute("data-bs-theme", "dark");
	} else {
		document.querySelector("html").setAttribute("data-bs-theme", "light");
	}
}

function listenForThemeChanges() {
	const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");

	mediaQueryList.addEventListener("change", (event) => {
		const newColorScheme = event.matches ? "dark" : "light";
		document.querySelector("html").setAttribute("data-bs-theme", newColorScheme);
		localStorage.setItem("theme", newColorScheme);
	});
}

setInitialTheme();
listenForThemeChanges();

document.querySelector("button.switch-theme").addEventListener("click", toggleTheme);