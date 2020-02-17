# -*- coding: utf-8 -*-
# Copyright 2017 mikaelh <https://github.com/mikaelh>
# Copyright 2017-2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT)
from openerp.addons.bus.controllers.main import BusController
from openerp.http import request


class MailChatController(BusController):
    # -----------------------------
    # Extends BUS Controller Poll
    # -----------------------------

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels = list(channels)  # do not alter original list
            channels.append((request.db, "mail_base.mail_sent"))

        return super(MailChatController, self)._poll(dbname, channels, last, options)
