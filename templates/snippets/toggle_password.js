$(document).ready(function () {
    $("span#toggle-password").on("click", function () {
        const passwordField = $(this).closest("div.form-group").find("input");
        const isPassword = passwordField.attr("type") === "password";
        passwordField.attr("type", isPassword ? "text" : "password");
        $(this).text(isPassword ? "visibility_off" : "visibility");
    });

    $("input[type='password']").on("keyup", function () {
        const toggleButton = $(this).closest("div.form-group").find("span#toggle-password");
        toggleButton.toggle($(this).val() !== "");
    });
});
