$(document).ready(function () {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications/`);

    let currentPage = 1;
    const perPage = 4;
    let fetching = false;
    const $div_notif_ul = $("div#notifications > ul");

    function renderNotifications(notifications, shouldPrepend) {
        if (Array.isArray(notifications) || typeof notifications === 'object') {
            if (!Array.isArray(notifications)) {
                notifications = [notifications];
            }

            if (notifications.length > 0) {
                const count = notifications[0].count || 0;
                $("span#red-dot").removeClass("d-none").addClass("d-block").text(count > 0 ? count : "");
            }

            const existingNotificationIds = new Set($div_notif_ul.find("li").map(function () {
                return this.dataset.id;
            }).get());

            notifications.forEach(notification => {
                const { id, type, from_user, created_at, action, seen } = notification;
                const seenClass = (seen === "False" ? "unseen" : "seen");
                if (existingNotificationIds.has(id)) {
                    $(`li[data-id="${id}"] > div > div > span#timestamp`).text(created_at);
                    $(`li[data-id="${id}"] > div > div > span#indicator`)
                        .removeClass(`text-${seen === "False" ? "success" : "danger"}`)
                        .addClass(`text-${seen === "False" ? "danger" : "success"}`);
                } else {
                    const notificationHTML = 
                    `<li data-id="${id}">
                        <div class="dropdown-item ${seenClass} d-flex flex-column align-items-end position-relative">
                            <a target="_blank" href="/account/profile/${from_user}">${action}</a>
                            ${type === "friend_request_notification" ? `
                                <div class="d-flex justify-content-between w-50">
                                    <button value="${from_user}" class="btn btn-sm" role="button" type="button" id="accept-fr-btn">
                                        <span class="material-icons text-success">check</span>
                                    </button>
                                    <button value="${from_user}" class="btn btn-sm" role="button" type="button" id="reject-fr-btn">
                                        <span class="material-icons text-danger">close</span>
                                    </button>
                                </div>` : ""}
                            <div class="w-100 d-flex align-items-center justify-content-between">
                                <span id="indicator" class="material-icons" style="font-size:10px;">radio_button_checked</span>
                                <span id="timestamp" class="small float-end">${created_at}</span>
                            </div>
                        </div>
                    </li>`;                    
                    if (shouldPrepend) {
                        $div_notif_ul.prepend(notificationHTML);
                    } else {
                        $div_notif_ul.append(notificationHTML);
                    }
                }
            });
        } else {
            $("span#red-dot").addClass("d-none");
            $div_notif_ul.html(`<li class="p-1 text-center">No Notifications Yet</li>`);
        }
    }


    function fetchNotifications(page, perPage) {
        if (!fetching) {
            fetching = true;
            socket.send(JSON.stringify({
                'command': 'fetch_notifications',
                'page': page,
                'per_page': perPage
            }));
        }
    }

    function markNotificationSeen(id) {
        socket.send(JSON.stringify({
            'command': 'mark_seen',
            'id': id
        }));
    }

    socket.onopen = function () {
        fetchNotifications(currentPage, perPage);
        setInterval(fetchNotifications, 2000, 1, perPage);
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.notifications !== undefined) {
            renderNotifications(data.notifications, false);
            updatePagination(data.pagination);
        } else if (data.status === "success" && data.notification) {
            renderNotifications(data.notification, true);
        } else {
            $("span#red-dot").addClass("d-none");
            $div_notif_ul.html(`<li class="p-1 text-center">No Notifications Yet</li>`);
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
        const $this = $(this);
        const scrollTop = $this.scrollTop();
        const scrollHeight = $this[0].scrollHeight;
        const height = $this.height();
        if (scrollTop + height >= scrollHeight - 60) {
            console.log(!fetching, "scroll");
            
            if (!fetching) {
                ++currentPage;
                fetchNotifications(currentPage, perPage);
            }
        }
    }

    $div_notif_ul.on("click", "button#accept-fr-btn", function (e) {
        e.preventDefault();
        const id = $(this).parent().parent().parent()[0].dataset.id;
        socket.send(JSON.stringify({
            "command": "accept_fr",
            "user": $(this)[0].value,
            "id": id
        }));
    });

    $div_notif_ul.on("click", "button#reject-fr-btn", function (e) {
        e.preventDefault();
        const id = $(this).parent().parent().parent()[0].dataset.id;
        socket.send(JSON.stringify({
            "command": "reject_fr",
            "user": $(this)[0].value,
            "id": id
        }));
    });

    $div_notif_ul.on("click", "li", function (e) {
        const $this = $(this);
        const id = $this[0].dataset.id;
        if ($this.find("div").hasClass("unseen")) {
            markNotificationSeen(id);
        }
    });
});
