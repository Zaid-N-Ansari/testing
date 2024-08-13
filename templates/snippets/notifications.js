$(document).ready(function () {
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const notificationWS = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications/`);

    let currentPage = 1;
    const perPage = 4;
    let fetching = false;
    const $div_notif_ul = $("div#notifications > ul");
    const existingIds = new Set();
    let isNewNotification = false;

    function makeNewLiElm(id, type, from_user, created_at, action, seen) {
        const seenClass = (seen === "True" ? "seen" : "unseen");

        const li = document.createElement("li");
        li.setAttribute("data-id", id);

        const dropdownItem = document.createElement("div");
        dropdownItem.classList.add("dropdown-item", seenClass, "d-flex", "flex-column", "align-items-end", "position-relative");

        const link = document.createElement("a");
        link.setAttribute("target", "_blank");
        link.setAttribute("href", `/account/profile/${from_user}`);
        link.textContent = action;

        dropdownItem.appendChild(link);

        if (type === "friend_request_notification") {
            const friendAction = document.createElement("div");
            friendAction.id = "friend-action";
            friendAction.classList.add("d-flex", "justify-content-between", "w-50");

            const acceptButton = document.createElement("button");
            acceptButton.setAttribute("value", from_user);
            acceptButton.classList.add("btn", "btn-sm");
            acceptButton.setAttribute("role", "button");
            acceptButton.setAttribute("type", "button");
            acceptButton.id = "accept-fr-btn";
            acceptButton.innerHTML = "<span class='material-icons text-success'>check</span>";

            const rejectButton = document.createElement("button");
            rejectButton.setAttribute("value", from_user);
            rejectButton.classList.add("btn", "btn-sm");
            rejectButton.setAttribute("role", "button");
            rejectButton.setAttribute("type", "button");
            rejectButton.id = "reject-fr-btn";
            rejectButton.innerHTML = "<span class='material-icons text-danger'>close</span>";

            friendAction.appendChild(acceptButton);
            friendAction.appendChild(rejectButton);

            dropdownItem.appendChild(friendAction);
        }

        const utils = document.createElement("div");
        utils.id = "utils";
        utils.classList.add("w-100", "d-flex", "align-items-center", "justify-content-between");

        const indicator = document.createElement("span");
        indicator.id = "indicator";
        indicator.classList.add("material-icons", seen === "True" ? "text-success" : "text-danger");
        indicator.style.fontSize = "10px";
        indicator.textContent = "radio_button_checked";

        const timestamp = document.createElement("span");
        timestamp.id = "timestamp";
        timestamp.classList.add("float-end");
        timestamp.style.fontSize = "small";
        timestamp.textContent = created_at;

        utils.appendChild(indicator);
        utils.appendChild(timestamp);

        dropdownItem.appendChild(utils);

        li.appendChild(dropdownItem);

        return li;
    }

    function renderNotifications(notifications, isNew) {
        if (Array.isArray(notifications)) {
            notifications.forEach(notification => {
                const { id, type, from_user, created_at, action, count, seen } = notification;
                $("span#counter").text(count);

                if (existingIds.has(id)) {
                    if (type === "regular_notification") {
                        $(`li[data-id="${id}"] > div > div#friend-action`).html("");
                    }

                    $(`li[data-id="${id}"] > div > div > span#timestamp`).text(created_at);
                    $(`li[data-id="${id}"] > div > div > span#indicator`)
                        .removeClass(`text-${seen === "False" ? "success" : "danger"}`)
                        .addClass(`text-${seen === "False" ? "danger" : "success"}`);
                } else {
                    const newNotification = makeNewLiElm(id, type, from_user, created_at, action, seen);

                    if (isNew) {
                        $div_notif_ul[0].insertBefore(newNotification, $div_notif_ul[0].firstChild);
                    } else {
                        $div_notif_ul[0].appendChild(newNotification);
                    }
                    existingIds.add(id);
                }
            });
        }
    }

    function fetchNotifications(page, perPage) {
        if (!fetching) {
            fetching = true;
            notificationWS.send(JSON.stringify({
                "command": "fetch_notifications",
                "page": page,
                "per_page": perPage
            }));
        }
    }

    function markNotificationSeen(id) {
        notificationWS.send(JSON.stringify({
            "command": "mark_seen",
            "id": id
        }));
    }

    notificationWS.onopen = function () {
        fetchNotifications(currentPage, perPage);
        setInterval(() => {
            isNewNotification = true;
            fetchNotifications(1, perPage);
        }, 3000);
    };

    notificationWS.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.notifications !== undefined) {
            renderNotifications(data.notifications, isNewNotification);
            updatePagination(data.pagination);
            isNewNotification = false;
        }

        if (data.status === "success" && data.notification) {
            renderNotifications(data.notification, true);
        }

        fetching = false;
    };

    function updatePagination({ current_page, total_pages }) {
        if (current_page < total_pages) {
            $div_notif_ul.on("scroll", handleScroll);
        } else {
            $div_notif_ul.off("scroll", handleScroll);
        }
    }

    function handleScroll() {
        if ($(this).scrollTop() + $(this).height() >= $(this)[0].scrollHeight - 10 && !fetching) {
            ++currentPage;
            fetchNotifications(currentPage, perPage);
        }
    }

    $div_notif_ul.on("click", "button#accept-fr-btn, button#reject-fr-btn", function (e) {
        e.preventDefault();
        const id = $(this).closest("li")[0].dataset.id;
        const command = (this.id === "accept-fr-btn" ? "accept_fr" : "reject_fr");

        notificationWS.send(JSON.stringify({
            "command": command,
            "user": $(this)[0].value,
            "id": id
        }));
    });

    $div_notif_ul.on("click", "li", function () {
        const $this = $(this);
        const id = $this[0].dataset.id;

        if ($this.find("div").hasClass("unseen")) {
            markNotificationSeen(id);
            $this.find("div").removeClass("unseen").addClass("seen");
        }
    });
});