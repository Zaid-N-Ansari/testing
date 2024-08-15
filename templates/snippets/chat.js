$(document).ready(function () {
	const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
	const chatWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/{{room}}`);
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
				"command": "send",
				"message": textMsg.val()
			}));
		}
	});
});