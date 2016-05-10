odoo.define('res_partner_mails_count.res_partner_mails_count_tour', function (require) {
    'use strict';
    var Core = require('web.core');
    var Tour = require('web.Tour');
    var _t = Core._t;

    Tour.register({
        id: 'mails_count_tour',
        name: _t("Mails count Tour"),
        mode: 'test',
        path: '/web?res_partner_mails_count=tutorial#id=3&view_type=form&model=res.partner',
        steps: [
            {
                title:     _t("Mails count tutorial"),
                content:   _t("Let's see how mails count work."),
                popover:   { next: _t("Start Tutorial"), end: _t("Skip") },
            },
            {
                title:     _t("New fields"),
                content:   _t("Here is new fields with mails counters. Press one of it."),
                element:   '.mails_to',
                waitFor:   '.mails_to:visible',
            },
            {
                title: _t("Done"),
                placement: 'top',
                waitNot: '.mails_to:visible',
                waitFor: '.o_mail_thread',
                element: '.o_mail_thread',
                content: _t("Message are found. <br/>Enjoy your day! <br/> <br/><a href='https://www.it-projects.info/apps' target='_blank'>IT-Projects LLC</a> team "),
                popover: {next: _t("Close Tutorial")},
            },
        ]
    });

});
