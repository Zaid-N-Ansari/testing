$(document).ready(function (e) {
	$("span.span_edit").css("opacity", "0");
	$("div.edit").on("mouseenter", function (e) {
		$(this).children("img.img_edit").css({
			"opacity": "0.8",
			"transition": "opacity 200ms ease"
		});
		$(this).children("span.span_edit").css({
			"cursor": "pointer",
			"opacity": "1",
			"transition": "opacity 200ms ease"
		});
	});
	$("div.edit").on("mouseleave", function (e) {
		$(this).children("img.img_edit").css("opacity", "1");
		$(this).children("span.span_edit").css("opacity", "0");
	});
	$("span.span_edit").on("click", function () {
		$("input[type='file']").click();
	});

	function isImgSizeValid(img) {
		var startIndex = img.indexOf("base64,") + 7;
		var base64Str = img.substr(startIndex);
		var decode = atob(base64Str);
		if (decode.length >= 10485760) {
			alert("Image File Size Exceded, should not be greater than 10 MB");
			return null;
		}
		return base64Str;
	}

	function readURL(input) {
		if (input.files && input.files[0]) {
			const reader = new FileReader();
			reader.onload = function (e) {
				let image = e.target.result;
				const imageField = $("img")[1];
				imageField.src = image;
				const cropper = new Cropper(imageField, {
					aspectRatio: 1,
					viewMode: 1,
					crop(event) {
						$("span.span_edit").css("display", "none");
						$("span.point-se").css({
							"height": "5px",
							"width": "5px",
						});
						let x = parseFloat(event.detail.x);
						let y = parseFloat(event.detail.y);
						let s = parseFloat(event.detail.height);
						$("#id_x").val(x);
						$("#id_y").val(y);
						$("#id_s").val(s);
						$("#id_image").val(isImgSizeValid(image));
					}
				});
			};
			reader.readAsDataURL(input.files[0]);
		}
	}
});