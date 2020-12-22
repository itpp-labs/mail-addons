/*  Copyright 2018 Artem Rafailov <https://it-projects.info/team/KolushovAlexandr>
    License MIT (https://opensource.org/licenses/MIT).*/
odoo.define("mail_to.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require("web.core");
    var _t = core._t;

    var steps = [
        {
            trigger: "a.recipient_link:first",
            content: _t("Open Partners Form From Recipient Link"),
            position: "bottom",
            timeout: 70000,
        },
    ];

    tour.register("mail_to_tour", {test: true, url: "/web"}, steps);
});
