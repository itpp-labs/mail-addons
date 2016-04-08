import openerp.tests

@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):
    def test_01_res_partner_mails_count(self):
        link = "/web?debug=1&amp;res_partner_mails_count=tutorial#id=3&amp;view_type=form&amp;model=res.partner&amp;/#tutorial_extra.mails_count_tour=true"
        self.phantom_js('/',  "openerp.Tour.run('mails_count_tour', 'test')", "openerp.Tour.tours.mails_count_tour", login="admin")
