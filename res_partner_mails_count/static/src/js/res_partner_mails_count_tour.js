(function () {
    'use strict';

    var _t = openerp._t;

    openerp.Tour.register({
        id: 'mails_count_tour',
        name: _t("Mails count Tour"),
        mode: 'test',
        path: '/web?res_partner_mails_count=tutorial#id=3&view_type=form&model=res.partner',
        // mode: 'tutorial',
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
                
            },
            {
                waitNot:   '.mails_to:visible',
                title:     _t("Check messages or send new one"),
                placement: 'left',
                content:   _t("Click <em>'Send a mesage'</em> to continue the Tour"),
                element:   '.oe_mail_wall .oe_msg.oe_msg_composer_compact>div>.oe_compose_post',
            },
            {
                title: _t("Done"),
                placement: 'top',
                waitNot: '.mails_to:visible',
                element: 'div.oe_msg_content>textarea.field_text',
                content: _t("Message are found. <br/>Enjoy your day! <br/> <br/><a href='https://www.it-projects.info/apps' target='_blank'>IT-Projects LLC</a> team "),
                popover: {next: _t("Close Tutorial")},
            },
        ]
    });

}());
