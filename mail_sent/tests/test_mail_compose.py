# Copyright 2020 Denis Mudarisov <https://github.com/trojikman>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "at_install")
class TestSaas(HttpCase):
    def test_mail_compose(self):
        # this is enough to reproduce the error
        # from https://github.com/itpp-labs/mail-addons/issues/290
        self.env["mail.compose.message"].create({})
