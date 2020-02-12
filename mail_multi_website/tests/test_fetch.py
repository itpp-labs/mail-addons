# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tools import mute_logger

from odoo.addons.test_mail.data.test_mail_data import MAIL_TEMPLATE
from odoo.addons.test_mail.tests.test_mail_mail import TestMail


class TestFetch(TestMail):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestFetch, self).setUp()
        self.website = self.env["website"].create(
            {"name": "Test Website", "domain": "example.com"}
        )
        self.company = self.env["res.company"].create({"name": "New Test Website"})
        self.website.company_id = self.company

        # copy-paste from mail.tests.test_mail_gateway
        mail_test_model = self.env["ir.model"]._get("mail.test.simple")
        # groups@.. will cause the creation of new mail.test
        self.alias = self.env["mail.alias"].create(
            {
                "alias_name": "groups",
                "alias_user_id": False,
                "alias_model_id": mail_test_model.id,
                "alias_contact": "everyone",
            }
        )

    @mute_logger("odoo.addons.mail.models.mail_thread", "odoo.models")
    def test_fetch_multi_website(self):
        """ Incoming email on an alias creating a new record + message_new + message details """
        new_groups = self.format_and_process(
            MAIL_TEMPLATE, subject="My Frogs", to="groups@example.com, other@gmail.com"
        )

        # Test: one group created by mailgateway administrator
        self.assertEqual(
            len(new_groups),
            1,
            "message_process: a new mail.test should have been created",
        )
        self.assertEqual(
            new_groups.website_id,
            self.website,
            "New record is created with wrong website",
        )
        self.assertEqual(
            new_groups.company_id,
            self.company,
            "New record is created with wrong company",
        )
