/*  # Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define("mail_all.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require("web.core");
    var _t = core._t;

    var steps = [
        {
            trigger: 'a.full[href="#"]',
            content: _t("Click to open app list"),
            position: "bottom",
        },
        {
            trigger: 'a.dropdown-item.o_app:contains("Discuss")',
            content: _t("Click to enter menu discuss"),
            position: "bottom",
        },
        {
            content: _t("Open All Messages"),
            trigger: ".o_channel_name.mail_all",
        },
        {
            content: _t("Check that All Messages are opened"),
            trigger:
                ".o_mail_discuss_title_main.o_mail_mailbox_title_all.o_mail_discuss_item.o_active",
        },
    ];

    tour.register("tour_mail_all", {test: true, url: "/web"}, steps);
});
