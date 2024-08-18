$(document).ready(function () {
    const cardHeader = $("h5.card-header").eq(1);
    const cardBody = $("div.card-body").eq(1);
    const cardTools = $("div.card-tools");
    const cardBodyButton = $("div.card > div.card-body > button");
    let chatWS;

    cardBody.scrollTop(cardBody[0].scrollHeight);

    cardHeader.text("Welcome to ChatApp, Happy Chatting...");
    cardTools.removeClass("d-flex").addClass("d-none");

    $(this).on("keyup", function (event) {
        if (event.key === "Escape" || event.keyCode === 27) {
            if (chatWS) {
				chatWS.close();
			}
            cardBodyButton.removeClass("active");
            cardHeader.text("Welcome to ChatApp, Happy Chatting...");
            cardBody.empty();
            cardTools.removeClass("d-flex").addClass("d-none");
        }
    });

    cardBodyButton.on("click", function () {
        const req = {
            "csrfmiddlewaretoken": "{{ csrf_token }}",
            "user_to_connect": $(this).data().id,
        };
        console.log(req);
		if (chatWS) {
			chatWS.close();
		}

        cardBodyButton.removeClass("active");
        $(this).addClass("active");

        $.post("{% url 'chat:personal' %}", req, function ({ to, room }) {
            console.log({ to, room });
            intializeChatWS(room);
            cardHeader.empty();
            cardBody.empty();
            cardHeader.append(`
                <span>${to}</span>
                <span data-toggle="tooltip" data-placement="left" title="Connecting..." class="material-icons status-icon" style="font-size: 1rem; cursor: default;">radio_button_checked</span>
            `);
            cardTools.removeClass("d-none").addClass("d-flex");
        });
    });

    function intializeChatWS(room) {
        const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
        chatWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/${room}`);
        const textMsg = $("textarea#input-msg");

        chatWS.onopen = function () {
            console.log("chatWS OPENED");
        };

        chatWS.onclose = function () {
            console.log("chatWS CLOSED");
        };

        chatWS.onerror = function () {
            console.log("chatWS ERROR");
        };

        chatWS.onmessage = function (event) {
            const data = JSON.parse(event.data);
            const statusIcon = cardHeader.find("span.status-icon");

            console.log(data);

            if (data.type === "status_update") {
                if (data.participants_count > 1) {
                    statusIcon.removeClass("text-danger").addClass("text-success");
                } else {
                    statusIcon.removeClass("text-success").addClass("text-danger");
                }
            }

            if (data.type === "incoming") {
                cardBody.append(`
                    <div class="bubble ${data.from_user==="{{request.user}}"?"right":"left"}">${data.message}</div>
                `);
            }
        };

        $("button#send-msg-btn").on("click", function () {
            if (chatWS.readyState === WebSocket.OPEN) {
                chatWS.send(JSON.stringify({
                    "command": "send_message",
                    "message": textMsg.val()
                }));
            }
        });
    }
});
