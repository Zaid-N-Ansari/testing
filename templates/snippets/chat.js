$(document).ready(function () {
	const cardHeader = $("h5.card-header").eq(1);
	const cardBody = $("div.card-body").eq(1);
	const cardTools = $("div.card-tools");
	const cardBodyButton = $("div.card > div.card-body > button");

	cardHeader.text("Welcome to ChatApp, Happy Chatting...");
	cardTools.removeClass("d-flex").addClass("d-none");

	$(this).on("keyup", function (event) {
		if (event.key === "Escape" || event.keyCode === 27) {
			cardBodyButton.removeClass("active");
			cardHeader.text("Welcome to ChatApp, Happy Chatting...");
			cardBody.empty();
			cardTools.removeClass("d-flex").addClass("d-none");
		}
	});

	cardBodyButton.on("click", function () {
		const req = {
			"user_to_connect": $(this).data().id,
		};

		cardBodyButton.removeClass("active");
		$(this).addClass("active");

		$.get(`/chat/${req.user}/`, req, function ({ to, room }) {
			console.log({ to, room });
			intializeChatWS(room);
			cardHeader.empty();
			cardBody.empty();
			cardHeader.append(`
					<span>${to}</span>
					<span data-toggle="tooltip" data-placement="left" title="Connecting..." class="material-icons" style="font-size: 1rem; cursor:default;">radio_button_checked</span>
				`);
			cardTools.removeClass("d-none").addClass("d-flex");
		});
	});
	function intializeChatWS(room) {
		const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
		const chatWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/${room}`);
		const textMsg = $("textarea#input-msg");

		chatWS.onopen = function () {
			console.log("chatWS OPENED");
		}
		chatWS.close = function () {
			console.log("chatWS CLOSED");
		}
		chatWS.error = function () {
			console.log("chatWS ERROR");
		}
		chatWS.onmessage = function () {
			const data = JSON.parse(event.data);

			if (data.message) {
				console.log(data.message);
			}
		}

		$("button#send-msg-btn").on("click", function () {
			if (chatWS.OPEN) {
				chatWS.send(JSON.stringify({
					"command": "send_message",
					"message": textMsg.val()
				}));
			}
		});
	}
});