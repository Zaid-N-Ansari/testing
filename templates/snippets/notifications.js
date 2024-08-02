$(document).ready(function () {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications/`);

    let currentPage = 1;
    const perPage = 2;
    let fetching = false;
    const $div_notif_ul = $("div#notifications > ul");

    function displayNotifications(data) {
        const { notifications } = data;
        if (notifications.length > 0) {
            $("span#red-dot").addClass("d-block").text(notifications[0].count > 0 ? notifications[0].count : "");

            const existingNotificationIds = new Set($div_notif_ul.find("li").map(function () {
                return this.dataset.id;
            }).get());
            notifications.forEach(notification => {
                const { pfi, id, from_user, created_at, action, seen } = notification;
                const seenClass = seen === "False" ? "unseen" : "seen";

                if (existingNotificationIds.has(id)) {
                    $(`li[data-id="${id}"] > div > span#timestamp`).text(created_at);

                    $div_notif_ul.find(`li[data-id="${id}"] > div > div > span#indicator`)
                        .text(seenClass.replace(/unseen|seen/, match => match === "unseen" ? "UnSeen" : "Seen"))
                        .removeClass(`text-${seen === "False" ? "success" : "danger"}`)
                        .addClass(`text-${seen === "False" ? "danger" : "success"}`);
                } else {
                    $div_notif_ul.append(`
                        <li data-id="${id}">
                            <div class="dropdown-item ${seenClass} d-flex flex-column align-items-end position-relative">
                                <a target="_blank" href="/account/profile/${from_user}">${action}</a>
                                <div class="d-flex justify-content-between w-50">
                                    <button value="${from_user}" class="btn btn-sm" role="button" type="button" id="accept-fr-btn">
                                        <span class="material-icons text-success">check</span>
                                    </button>
                                    <button value="${from_user}" class="btn btn-sm" role="button" type="button" id="reject-fr-btn">
                                        <span class="material-icons text-danger">close</span>
                                    </button>
                                </div>
                                <div class="w-100">
                                    <span id="indicator" class="small text-danger">UnSeen</span>
                                    <span id="timestamp" class="small float-end">${created_at}</span>
                                </div>
                            </div>
                        </li>
                    `);
                }
            });
        } else {
            $("span#red-dot").addClass("d-none");
            $div_notif_ul.addClass("px-1 text-center").html(`
                <li>
                    <span>No Notifications Yet</span>
                </li>
            `);
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

    function markAllSeen(id) {
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

        if (data.notifications) {
            displayNotifications(data);
            updatePagination(data.pagination);
        } else if (data.status === 'success' && data.message) {
            console.log(data.message);
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
        if (scrollTop + height >= scrollHeight - 20) {
            if (!fetching) {
                currentPage++;
                fetchNotifications(currentPage, perPage);
            }
        }
    }

    $div_notif_ul.on("click", "button#accept-fr-btn", function() {
        socket.send(JSON.stringify({
            "command": "accept_fr",
            "user": $(this)[0].value
        }));
    });

    $div_notif_ul.on("click", "li", function (e) {
        const $this = $(this);
        const id = $this[0].dataset.id;
        if ($this.find("div").hasClass("unseen")) {
            markAllSeen(id);
        }
    });
});
