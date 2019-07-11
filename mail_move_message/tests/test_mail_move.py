# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests
from odoo.api import Environment


@odoo.tests.common.at_install(True)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):

    def test_create_new_partner_and_move_message(self):
        env = Environment(self.registry.test_cr, self.uid, {})
        # needed because tests are run before the module is marked as
        # installed. In js web will only load qweb coming from modules
        # that are returned by the backend in module_boot. Without
        # this you end up with js, css but no qweb.
        env['ir.module.module'].search([('name', '=', 'mail_move_message')], limit=1).state = 'installed'
        self.registry.cursor().release()

        # updating models, to be able relocate messages to a partner at_install
        config_parameters = self.env["ir.config_parameter"].sudo()
        config_parameters.set_param("mail_relocation_models", "crm.lead,project.task,res.partner")

        code = """
                    var delayed_button_click = function(delay, button){
                        setTimeout(function(){
                            if (button.length) {
                                return button.click();
                            }
                            return console.log('error', 'There is no element with the next selector: ' + button.selector);
                        }, delay);
                    };
                    var delay = 1000;
                    var message = $('.o_thread_message_core:contains("virginie")');
                    var relocate = message.find('.o_thread_icons .fa-exchange');
                    delayed_button_click(delay, relocate);
                    // form is opened

                    var create_partner_button = $('button[special="quick_create"]');
                    delayed_button_click(delay, create_partner_button);
                    // partner creation wizard is opened

                    var save_button = $('.modal-content .btn-primary:contains("Save")');
                    delayed_button_click(delay, save_button);

                    var move_button = $('.btn-sm.oe_highlight:contains("Move")');
                    delayed_button_click(delay, move_button);
                    console.log('ok')
        """

        self.phantom_js('/web', code, login="admin", ready="$('.o_thread_icons').length")
