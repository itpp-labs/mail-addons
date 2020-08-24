/*  Copyright 2018 Artem Rafailov <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).*/
odoo.define("mail_to.tour", function(require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require("web.core");
    var _t = core._t;

    var steps = [
        tour.STEPS.SHOW_APPS_MENU_ITEM,
        {
            trigger: '.o_app[data-menu-xmlid="mail.menu_root_discuss"]',
            content: _t(
                "Want to <b>get in touch</b> with your contacts? <i>Discuss with them here.</i>"
            ),
            position: "right",
            edition: "community",
        },
        {
            trigger: '.fa.fa-plus.o_add[data-type="public"]',
            position: "right",
            edition: "community",
            run: function(actions) {
                $(".o_input.ui-autocomplete-input").val(
                    "Channel #" + String(new Date().getTime())
                );
                $(".o_input.ui-autocomplete-input").keydown();
                setTimeout(function() {
                    $(".ui-menu-item > a").click();
                }, 1000);
            },
        },
        {
            trigger: "a.recipient_link:first",
            content: _t("Open Partners Form From Recipient Link"),
            position: "bottom",
        },
    ];

    tour.register("mail_to_tour", {test: true, url: "/web"}, steps);
});
