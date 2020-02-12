# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 manawi <https://it-projects.info/team/manawi>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_mail_all(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        self.env["ir.module.module"].search(
            [("name", "=", "mail_all")], limit=1
        ).state = "installed"

        link = "/web#action=%s" % self.ref("mail.action_discuss")
        self.phantom_js(
            link,
            "odoo.__DEBUG__.services['web_tour.tour'].run('tour_mail_all', 1000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.tour_mail_all.ready",
            login="admin",
        )
