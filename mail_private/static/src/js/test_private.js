/*  Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).*/
odoo.define('mail_private.tour', function(require) {
"use strict";

    var core = require('web.core');
    var tour = require('web_tour.tour');
    var _t = core._t;

    var email = 'mail_private test email';
    var steps = [tour.STEPS.SHOW_APPS_MENU_ITEM, {
            trigger: '.fa.fa-cog.o_mail_channel_settings',
            content: _t('Select channel settings'),
            position: 'bottom',
        }, {
            trigger: '.nav-link:contains("Members")',
            content: _t('Go to the list of subscribers'),
            position: 'bottom',
        }, {
            trigger: '.o_data_cell:contains("YourCompany, Marc Demo")',
            content: _t("Select a user"),
            position: "bottom",
        }, {
            trigger: '.o_form_uri.o_field_widget:contains("YourCompany, Marc Demo")',
            content: _t("Go to user page"),
            position: "bottom"
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
            trigger: "div.o_composer_suggested_partners",
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
