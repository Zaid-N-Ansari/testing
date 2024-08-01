$(document).ready(function () {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications/`);

    let currentPage = 1;
    const perPage = 2;
    let fetching = false;
    const $div_notif_ul = $("div#notifications > ul");

    function displayNotifications(data) {
        const { notifications } = data;
        console.log(notifications);

        if (notifications.length > 0) {
            $("span#red-dot").addClass("d-block").text(notifications[0].count > 0 ? notifications[0].count : '');

            const existingNotificationIds = new Set($div_notif_ul.find("li").map(function () {
                return this.dataset.id;
            }).get());

            notifications.forEach(notification => {
                const { id, from_user, created_at, action, seen } = notification;
                const seenClass = seen === "False" ? 'unseen' : 'seen';

                if (existingNotificationIds.has(id)) {
                    $(`li[data-id="${id}"] > div > span`).eq(0).text(created_at);
                } else {
                    $div_notif_ul.append(`
                        <li data-id="${id}">
                            <div class="dropdown-item px-2 text-end ${seenClass}">
                                <a target="_blank" class="text-end" href="/account/profile/${from_user}">${action}</a>
                                <span class="small float-end">${created_at}</span>
                                <span class="d-block w-50 float-end">
                                    <span class="text-decoration-underline small text-reset material-icons float-start">check</span>
                                    <span class="text-decoration-underline small text-reset material-icons float-end pe-5">close</span>
                                </span>
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

    function markAllSeen() {
        socket.send(JSON.stringify({
            'command': 'mark_seen'
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
        console.log(current_page, perPage, total_pages);
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

    $("div#notifications > ul > li > div.dropdown-item").on("mouseover", function (e) {
        // const $this = $(this);
        // console.log($this);
        // if ($this.hasClass('unseen')) {
        //     markAllSeen();
        //     $this.removeClass('unseen').addClass('seen');
        // }
        alert(e)
    });
});
