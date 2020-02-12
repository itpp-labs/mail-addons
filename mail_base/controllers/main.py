from odoo.http import request

from odoo.addons.bus.controllers.main import BusController


class MailChatController(BusController):
    # -----------------------------
    # Extends BUS Controller Poll
    # -----------------------------

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels.append((request.db, "mail_base.mail_sent"))

        return super(MailChatController, self)._poll(dbname, channels, last, options)
