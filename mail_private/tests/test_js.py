# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_mail_private(self):
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        cr = self.registry.cursor()
        self.env["ir.module.module"].search(
            [("name", "=", "mail_private")], limit=1
        ).state = "installed"
        cr._lock.release()

        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('mail_private_tour', 1000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.mail_private_tour.ready",
            login="admin",
            timeout=90,
        )
