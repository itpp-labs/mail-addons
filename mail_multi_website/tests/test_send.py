# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase


class TestSendMail(TransactionCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestSendMail, self).setUp()
        self.website = self.env.ref("website.website2")
        self.company = self.env["res.company"].create({"name": "New Test Website"})
        self.original_email = self.env.user.email
        self.original_company = self.env.user.company_id
        self.email = "superadmin@second-website.example"
        # Check that current email is set and differs
        self.assertTrue(self.email)
        self.assertNotEqual(self.original_email, self.email)
        self.website.company_id = self.company

    def switch_user_website(self):
        # add website to allowed
        self.env.user.write(
            dict(
                backend_website_ids=[(4, self.website.id)],
                backend_website_id=self.website.id,
                company_id=self.company.id,
                company_ids=[(4, self.company.id)],
            )
        )

    def test_multi_email(self):
        """User has email addresses per website"""
        self.switch_user_website()
        # update user's email
        self.env.user.email = self.email
        # Check that writing works
        self.env.user.invalidate_cache()
        self.assertEqual(
            self.env.user.email,
            self.email,
            "Write methods doesn't work (Field is not in registry?)",
        )

        # changing company will automatically update website value to empty value
        self.env.user.company_id = self.original_company
        self.env.user.invalidate_cache()
        self.assertEqual(
            self.env.user.email,
            self.original_email,
            "Multi-email doesn't work on switching websites",
        )

    def test_multi_email_partner(self):
        """Partner doesn't have email addresses per website"""
        original_email = "original@email1"
        new_email = "new@email2"
        partner = self.env["res.partner"].create(
            {"name": "test", "email": original_email}
        )
        self.switch_user_website()
        # update partner's email
        partner.email = new_email
        self.assertEqual(partner.email, new_email)
        # changing company will automatically update website value to empty value
        self.env.user.company_id = self.original_company
        self.env.user.invalidate_cache()
        self.assertEqual(
            partner.email, new_email, "Partner's email must not be Multi-website"
        )
