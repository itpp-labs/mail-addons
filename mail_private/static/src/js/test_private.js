/*  Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).*/
odoo.define('mail_private.tour', function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require('web.core');
    var _t = core._t;

    var email = 'mail_private test email';
    var steps = [{
            trigger: '.o_thread_message strong.o_mail_redirect:contains("Agrolait")',
            content: _t("Open Partners Form"),
            position: 'bottom',
        }, {
            trigger: "button.oe_compose_post_private",
            content: _t("Click on Private mail creating button"),
            position: "bottom"
        }, {
            // for some reason (due to tricky renderings) button.oe_composer_uncheck could not be find by the tour manager
            trigger: ".o_control_panel.o_breadcrumb_full li.active",
            content: _t("Dummy action"),
        }, {
            trigger: "button.oe_composer_uncheck",
            extra_trigger: "button.oe_composer_uncheck",
            content: _t("Uncheck all Followers"),
            timeout: 10000,
        }, {
            trigger: "div.o_composer_suggested_partners input:first",
            content: _t("Check the first one"),
        }, {
            trigger: "textarea.o_composer_text_field:first",
            content: _t("Write some email"),
            run: function() {
                $('textarea.o_composer_text_field:first').val(email);
            },
        }, {
            trigger: ".o_composer_send .o_composer_button_send",
            content: _t("Send email"),
        }, {
            trigger: ".o_mail_thread .o_thread_message:contains(" + email + ")",
            content: _t("Send email"),
        }
    ];

    tour.register('mail_private_tour', { test: true, url: '/web' }, steps);

});
