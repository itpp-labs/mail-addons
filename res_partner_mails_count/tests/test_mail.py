# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestMessageCount(TransactionCase):
    post_install = True

    def test_count(self):
        new_partner1 = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": "rpmc Test Partner one",
                    "email": "tt@tt",
                    "notify_email": "always",
                }
            )
        )
        new_partner2 = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": "rpmc Test Partner two",
                    "email": "rr@rr",
                    "notify_email": "always",
                }
            )
        )
        self.assertEqual(
            new_partner1.mails_to, 0, "rpmc: new partner have mails_to != 0"
        )
        mail_compose = self.env["mail.compose.message"]
        compose = mail_compose.with_context(
            {"default_composition_mode": "comment"}
        ).create(
            {
                "subject": "test subj",
                "body": "test body",
                "partner_ids": [(4, new_partner2.id)],
                "email_from": "tt@tt",
                "author_id": new_partner1.id,
            }
        )
        compose.send_mail()
        self.assertEqual(new_partner1.mails_to, 0)
        self.assertEqual(
            new_partner1.mails_from, 1, "rpmc: one message but mails_from != 1"
        )
        self.assertEqual(
            new_partner2.mails_to, 1, "rpmc: one message but mails_to != 1"
        )
        self.assertEqual(new_partner2.mails_from, 0)
        compose.send_mail()
        self.assertEqual(new_partner1.mails_to, 0)
        self.assertEqual(
            new_partner1.mails_from, 2, "rpmc: one message but mails_from != 2"
        )
        self.assertEqual(
            new_partner2.mails_to, 2, "rpmc: one message but mails_to != 2"
        )
        self.assertEqual(new_partner2.mails_from, 0)
