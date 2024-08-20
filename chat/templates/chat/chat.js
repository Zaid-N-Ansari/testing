$(document).ready(function () {
    hljs.highlightAll();
    const cardHeader = $("h5.card-header").eq(1);
    const cardBody = $("div.card-body").eq(1);
    const cardTools = $("div.card-tools");
    const cardBodyButton = $("div.card > div.card-body > button");
    const textArea = $("textarea#input-msg");
    let chatWS;
    let roomType;

    cardBody.scrollTop(cardBody[0].scrollHeight);

    cardHeader.text("Welcome to ChatApp, Happy Chatting...");
    cardTools.removeClass("d-flex").addClass("d-none");

    $(this).on("keyup", function (event) {
        if (event.shiftKey && event.keyCode === 13) {
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
            "user_or_group_to_connect": $(this).data().id,
        };
        let url;
        if ($(this).data().type === "group") {
            roomType = $(this).data().type;
            url = "{% url 'chat:group' %}";
        }
        else {
            roomType = $(this).data().type;
            url = "{% url 'chat:personal' %}";
        }
        $.post(url, req, function ({ to, room }) {
            setupAndInitializeChatArea(to, room);
        });
    });

    function setupAndInitializeChatArea(to, room) {
        intializeChatWS(room);
        getLast15Messages(room);
        cardHeader.empty();
        cardBody.empty();
        cardHeader.append(`
            <span>${to}</span>
            <div class="d-flex justify-content-between">
                <div class="d-none typing-indicator flex-row align-items-center me-5">
                    <span class="small me-2"><small></small></span>
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
                <span title="Connecting..." id="status-icon" class="material-icons text-danger d-flex small" style="cursor:default;"></span>
            </div>
        `);
        cardTools.removeClass("d-none").addClass("d-flex");
    }

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
            const typingIndicator = cardHeader.find("div > div.typing-indicator");
            console.log(data);

            if (data.type === "status_update") {
                const isGroup = roomType === "group";
                const connected = data.participants.length > 1;

                statusIcon.text(isGroup ? "person" : "radio_button_checked")
                    .toggleClass("text-success", connected)
                    .toggleClass("text-danger", !connected)
                    .attr("title", connected ? "Connected" : isGroup ? "" : "Disconnected");

                if (isGroup) {
                    statusIcon.append(`<span>${data.participants.length - 1}</span>`);
                }
            }

            if (data.type === "incoming") {
                const { message, from_user, timestamp } = data;
                cardBody.append(createNewMessageBubble(message, from_user, timestamp));
            }

            if (data.type === "typing" && data.from_user !== "{{ request.user }}") {
                typingIndicator.toggleClass(["d-none","d-flex"])
                    .find("span > small").text(data.message);
                setTimeout(() => typingIndicator.toggleClass(["d-none","d-flex"]), 1500);
            }
        };

        function createNewMessageBubble(message, from_user, timestamp) {
            const md = window.markdownit({
                highlight: function (str, lang = "text") {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return '<pre><code class="hljs">' +
                                hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                                '</code></pre>';
                        } catch (error) {
                            console.error("Highlight.js error:", error);
                        }
                    }
                    return '<pre><code class="hljs">' + md.utils.escapeHtml(str) + '</code></pre>';
                },
                linkify: true,
            });
            const newMessageBubble = document.createElement("div");
            newMessageBubble.classList.add("bubble", from_user === "{{request.user}}" ? "right" : "left");
            newMessageBubble.innerHTML = md.render(message);

            const timestampElm = document.createElement("small");
            timestampElm.classList.add("d-block", "text-end")
            timestampElm.innerText = timestamp;

            newMessageBubble.appendChild(timestampElm);

            return newMessageBubble;
        }

        textArea.on("keyup", function () {
            if (chatWS.readyState === WebSocket.OPEN && textArea.val().trim()) {
                chatWS.send(JSON.stringify({
                    "command": "typing"
                }));
            }
        });

        $("button#send-msg-btn").on("click", async function () {
            if (chatWS.readyState === WebSocket.OPEN && textArea.val().trim()) {
                await chatWS.send(JSON.stringify({
                    "command": "send_message",
                    "message": textArea.val().trim()
                }));
            }
            textArea.val("");
        });
    }
});
