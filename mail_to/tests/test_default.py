# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License MIT (https://opensource.org/licenses/MIT).
import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_mail_to(self):
        cr = self.registry.cursor()
        env = Environment(cr, self.uid, {})
        env["ir.module.module"].search(
            [("name", "=", "mail_to")], limit=1
        ).state = "installed"
        cr.release()

        self.phantom_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('mail_to_tour', 1000)",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.mail_to_tour.ready",
            login="admin",
            timeout=200,
        )
