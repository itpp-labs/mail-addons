# -*- coding: utf-8 -*-
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):

    # TODO test returns error "Timeout after 10000 ms"
#    def test_01_res_partner_mails_to_count(self):
#        self.phantom_js('/', "openerp.Tour.run('mails_count_tour', 'test')", "openerp.Tour.tours.mails_count_tour", login="admin")

    def test_02_res_partner_mails_from_count(self):
        # wait till page loaded and then click and wait again
        code = """
            setTimeout(function () {
                $(".mails_from").click();
                setTimeout(function () {console.log('ok');}, 3000);
            }, 3000);
        """
        link = '/web#id=3&view_type=form&model=res.partner'
        self.phantom_js(link, code, "openerp.Tour.tours.mails_count_tour", login="admin")
