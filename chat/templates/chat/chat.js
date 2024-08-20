$(document).ready(function () {
    hljs.highlightAll();
    const cardHeader = $("h5.card-header").eq(1);
    const cardBody = $("div.card-body").eq(1);
    const cardTools = $("div.card-tools");
    const cardBodyButton = $("div.card > div.card-body > button");
    const textArea = $("textarea#input-msg");
    let chatWS;

    cardBody.scrollTop(cardBody[0].scrollHeight);

    cardHeader.text("Welcome to ChatApp, Happy Chatting...");
    cardTools.removeClass("d-flex").addClass("d-none");

    $(this).on("keyup", function (event) {
        if(event.shiftKey && event.keyCode === 13) {
            $("button#send-msg-btn").click();
        }

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
        cardBody.empty();
        if (chatWS) {
            chatWS.close();
        }

        cardBodyButton.removeClass("active");
        $(this).addClass("active");

        const req = {
            "csrfmiddlewaretoken": "{{ csrf_token }}",
            "user_to_connect": $(this).data().id,
        };
        $.post("{% url 'chat:personal' %}", req, function ({ to, room }) {
            intializeChatWS(room);
            getLast15Messages(room);
            cardHeader.empty();
            cardBody.empty();
            cardHeader.append(`
                <span>${to}</span>
                <div class="d-flex justify-content-between">
                    <div class="d-none typing-indicator flex-row align-items-center me-5">
                        <span class="small me-2"><small>typing</small></span>
                        <div class="container-anime">
                            <div class="cube">
                                <div class="cube__inner"></div>
                            </div>
                            <div class="cube">
                                <div class="cube__inner"></div>
                            </div>
                            <div class="cube">
                                <div class="cube__inner"></div>
                            </div>
                        </div>
                    </div>
                    <span data-toggle="tooltip" data-placement="top" title="Disconnected" id="status-icon" class="material-icons text-danger" style="font-size: 1rem; cursor:default;">radio_button_checked</span>
                </div>
            `);
            cardTools.removeClass("d-none").addClass("d-flex");
        });
    });

    function getLast15Messages(room) {
        if (chatWS.readyState === WebSocket.OPEN) {
            chatWS.send(JSON.stringify({
                "command": "get_last_15_messages"
            }));
        }
    }

    function intializeChatWS(room) {
        const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
        chatWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/${room}`);

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
            const statusIcon = cardHeader.find("span#status-icon");
            console.log(data);

            if (data.type === "status_update") {
                if (data.participants.length > 1) {
                    statusIcon.removeClass("text-danger").addClass("text-success");
                    statusIcon[0].title = "Connected";
                } else {
                    statusIcon.removeClass("text-success").addClass("text-danger");
                    statusIcon[0].title = "Disconnected";
                }
            }

            if (data.type === "incoming") {
                const { message, from_user, timestamp } = data;
                let newMessageBubble = createNewMessageBubble(message, from_user, timestamp);
                cardBody.append(newMessageBubble);
            }

            if(data.type === "typing" && data.from_user !== "{{ request.user }}") {
                    cardHeader.find("div > div.typing-indicator").removeClass("d-none").addClass("d-flex");
                    setTimeout(() => {
                        cardHeader.find("div > div.typing-indicator").removeClass("d-flex").addClass("d-none");
                    }, 1000);
                }
        };

        function createNewMessageBubble(message, from_user, timestamp) {
            const md = window.markdownit({
				highlight: function (str, lang) {
					if (lang && hljs.getLanguage(lang)) {
						try {
							return '<pre><code class="hljs">' +
								hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
								'</code></pre>';
						} catch (__) { }
					}
					return '<pre><code class="hljs">' + md.utils.escapeHtml(str) + '</code></pre>';
				},
				linkify: true,
			});
            const newMessageBubble = document.createElement("div");
            newMessageBubble.classList.add("bubble", from_user === "{{request.user}}" ? "right" : "left");
            newMessageBubble.innerHTML = md.render(message);

            const timestampElm = document.createElement("small");
            timestampElm.innerText = timestamp;

            newMessageBubble.appendChild(timestampElm);

            return newMessageBubble;
        }

        textArea.on("keypress", function() {
            if (chatWS.readyState === WebSocket.OPEN) {
                chatWS.send(JSON.stringify({
                    "command": "typing"
                }));
            }
        });

        $("button#send-msg-btn").on("click", function () {
            if (chatWS.readyState === WebSocket.OPEN) {
                chatWS.send(JSON.stringify({
                    "command": "send_message",
                    "message": textArea.val()
                }));
                textArea.val("");
            }
        });
    }
});
