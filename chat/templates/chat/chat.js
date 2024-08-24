$(document).ready(function () {
    hljs.highlightAll();
    const cardHeader = $("h5.card-header").eq(1);
    const cardBody = $("div.card-body").eq(1);
    const cardTools = $("div.card-tools");
    const cardBodyButton = $("div.card > div.card-body > button");
    const textArea = $("textarea#input-msg");
    let chatWS, roomType, loading = false, currentPage = 1, perPage = 10, totalPages;

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
        } else {
            roomType = $(this).data().type;
            url = "{% url 'chat:personal' %}";
        }
        $.post(url, req, function ({ to, room }) {
            setupAndInitializeChatArea(to, room);
        });
    });

    $("button[data-id]").each(function () {
        if ($(this).data().id === location.search.split("=")[1]) {
            $(this).click();
        }
    });

    function setupAndInitializeChatArea(to, room) {
        initializeChatWS(room);
        cardHeader.empty();
        cardBody.empty();
        cardBody.on('scroll', handleScroll);
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

    function initializeChatWS(room) {
        const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
        chatWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/chat/${room}`);

        chatWS.onopen = () => getMessages(currentPage, perPage);
        chatWS.onclose = () => console.log("chatWS CLOSED");
        chatWS.onerror = () => console.log("chatWS ERROR");
        chatWS.onmessage = ({ data }) => {
            const { type, message, from_user, timestamp, participants, pagination } = JSON.parse(data);
            const statusIcon = cardHeader.find("span#status-icon");
            const typingIndicator = cardHeader.find("div > div.typing-indicator");

            if (type === "status_update") {
                const isGroup = roomType === "group";
                const connected = participants.length > 1;

                statusIcon.text(isGroup ? "person" : "radio_button_checked")
                    .toggleClass("text-success", connected)
                    .toggleClass("text-danger", !connected)
                    .attr("title", connected ? "Connected" : isGroup ? "" : "Disconnected");

                if (isGroup) {
                    statusIcon.append(`<span>${participants.length - 1}</span>`);
                }
            }

            if (type === "incoming") {
                cardBody.append(createNewMessageBubble(message, from_user, timestamp));
                cardBody.scrollTop(cardBody[0].scrollHeight);
            }

            if (type === "load_messages") {
                loading = false;
                displayMessages(JSON.parse(data).messages, pagination.total_pages);
                updatePagination(pagination);
            }

            if (type === "typing" && from_user !== "{{ request.user }}") {
                typingIndicator.toggleClass(["d-none", "d-flex"])
                    .find("span > small").text(message);
                setTimeout(() => typingIndicator.toggleClass(["d-none", "d-flex"]), 1500);
            }
        };
    }

    function createNewMessageBubble(message, from_user, timestamp) {
        const md = window.markdownit({
            highlight: function (str, lang) {
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

    function displayMessages(messages, totalPages) {
        const currentHeight = cardBody[0].scrollHeight;
        messages.forEach(msg => {
            const { message, from_user, created_at } = msg;
            cardBody.prepend(createNewMessageBubble(message, from_user, created_at));
        });
        cardBody.scrollTop(cardBody[0].scrollHeight - currentHeight);
    }

    function updatePagination(paginationData) {
        totalPages = paginationData.total_pages;
        currentPage = paginationData.current_page;

        if (currentPage < totalPages) {
            cardBody.on("scroll", handleScroll);
        } else {
            cardBody.off("scroll", handleScroll);
        }
    }

    function getMessages(page, size) {
        loading = true;
        chatWS.send(JSON.stringify({
            "command": "get_messages",
            "page_number": page,
            "page_size": size
        }));
    }

    function loadMoreMessages() {
        if (currentPage < totalPages) {
            ++currentPage;
            getMessages(currentPage, perPage);
        }
    }

    function handleScroll() {
        if (cardBody.scrollTop() <= 110 && !loading) {
            loadMoreMessages();
        }
    }
});