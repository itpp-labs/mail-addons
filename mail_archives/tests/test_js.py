import odoo.tests
from werkzeug import url_encode


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_01_mail_archives(self):

        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        self.env['ir.module.module'].search([('name', '=', 'mail_archives')], limit=1).state = 'installed'

        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                console.log($(".mail_archives").length && 'ok' || 'error');
            }, 3000);
        """
        link = '/web#%s' % url_encode({'action': 'mail.action_discuss'})
        self.phantom_js(link, code, "odoo.__DEBUG__.services['web_tour.tour'].tours.mail_tour.ready", login="admin")
