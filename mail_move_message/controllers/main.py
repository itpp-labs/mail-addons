# Copyright 2016 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.http import request

from odoo.addons.bus.controllers.main import BusController


class MailChatController(BusController):
    # -----------------------------
    # Extends BUS Controller Poll
    # -----------------------------

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels.append((request.db, "mail_move_message"))
            channels.append((request.db, "mail_move_message.delete_message"))
        return super(MailChatController, self)._poll(dbname, channels, last, options)
