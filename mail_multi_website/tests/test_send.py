# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase


class TestSendMail(TransactionCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestSendMail, self).setUp()
        self.website = self.env.ref('website.website2')
        self.company = self.env['res.company'].create({
            'name': 'New Test Website'
        })
        self.original_email = self.env.user.email
        self.original_company = self.env.user.company_id
        self.email = 'superadmin@second-website.example'
        # Check that current email is set and differs
        self.assertTrue(self.email)
        self.assertNotEqual(self.original_email, self.email)

        self.website.company_id = self.company
        # add website to allowed
        self.env.user.write(dict(
            backend_website_ids=[(4, self.website.id)],
            backend_website_id=self.website.id,
            company_id=self.company.id,
            company_ids=[(4, self.company.id)]
        ))
        # update email
        self.env.user.email = self.email

    def test_multi_email(self):
        # changing company will automatically update website value to empty value
        self.env.user.company_id = self.original_company
        self.assertEqual(self.env.user.email, self.original_email, 'Multi-email doesn\'t work on switching websites')
