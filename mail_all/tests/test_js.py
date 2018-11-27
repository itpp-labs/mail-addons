# Copyright 2016 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 manawi <https://it-projects.info/team/manawi>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_mail_all(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                $(".mail_all").click();
                setTimeout(function () {console.log('ok');}, 3000);
            }, 1000);
        """
        link = '/web#action=%s' % self.ref('mail.action_discuss')
        self.phantom_js(link, code, "odoo.__DEBUG__.services['mail_all.all']", login="admin")
