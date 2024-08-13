$(document).ready(function () {
	$("div.edit")
	.on("mouseenter", function () {
		$(this).children("img.img_edit").css({
			"opacity": "0.6",
			"transition": "opacity 200ms ease"
		});
		$(this).children("span.span_edit").css({
			"cursor": "pointer",
			"opacity": "1",
			"transition": "opacity 200ms ease"
		});
	})
	.on("mouseleave", function () {
		$(this).children("img.img_edit").css("opacity", "1");
		$(this).children("span.span_edit").css("opacity", "0");
	});

	$("span.span_edit")
	.css("opacity", "0")
	.on("click", function () {
		$("input[type='file']").click();
	});
});

function readImageFile(input) {
	const file = input.files[0];
	if (file) {
		if (file.size >= 10485760) {
			alert("Image Size maximum 10MB Size Exceded");
			return;
		}

		const validExt = ["jpeg", "jpg", "png", "avif", "bmp", "apng", "webp", "heif", "svg", "ico", "xbm", "tif", "tiff", "jfif", "svgz", "pjp", "pjpeg"];
		const ext = file.type.split("/")[1];

		if (!validExt.includes(ext)) {
			alert("InValid Image Format");
			return;
		}

		const reader = new FileReader();
		reader.onload = function (e) {
			let image = e.target.result;
			const imageField = $("img")[1];
			imageField.src = image;
			const imageData = image.split(",")[1];
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
					$("#id_image").val(imageData);
				}
			});
		};
		reader.readAsDataURL(file);
	}
}