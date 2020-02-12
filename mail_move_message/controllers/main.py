# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.bus.controllers.main import BusController
from odoo.addons.web.controllers.main import DataSet


class MailChatController(BusController):
    # -----------------------------
    # Extends BUS Controller Poll
    # -----------------------------

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels = list(channels)  # do not alter original list
            channels.append((request.db, "mail_move_message"))
            channels.append((request.db, "mail_move_message.delete_message"))
        return super(MailChatController, self)._poll(dbname, channels, last, options)


class DataSetCustom(DataSet):
    def _extend_name(self, model, records):
        Model = request.env[model]
        fields = Model.fields_get()
        contact_field = False
        for n, f in fields.iteritems():
            if f["type"] == "many2one" and f["relation"] == "res.partner":
                contact_field = n
                break
        partner_info = {}
        if contact_field:
            partner_info = Model.browse([r[0] for r in records]).read([contact_field])
            partner_info = {p["id"]: p[contact_field] for p in partner_info}
        res = []
        for r in records:
            if partner_info.get(r[0]):
                res.append(
                    (r[0], _("%s [%s] ID %s") % (r[1], partner_info.get(r[0])[1], r[0]))
                )
            else:
                res.append((r[0], _("%s ID %s") % (r[1], r[0])))
        return res

    @http.route("/web/dataset/call_kw/<model>/name_search", type="json", auth="user")
    def name_search(self, model, method, args, kwargs):
        context = kwargs.get("context")
        if context and context.get("extended_name_with_contact"):
            # add order by ID desc
            Model = request.env[model]
            search_args = list(kwargs.get("args") or [])
            limit = int(kwargs.get("limit") or 100)
            operator = kwargs.get("operator")
            name = kwargs.get("name")
            if Model._rec_name and (not name == "" and operator == "ilike"):
                search_args += [(Model._rec_name, operator, name)]
            records = Model.search(search_args, limit=limit, order="id desc")
            res = records.name_get()
            return self._extend_name(model, res)

        return self._call_kw(model, method, args, kwargs)

    @http.route("/web/dataset/call_kw/<model>/name_get", type="json", auth="user")
    def name_get(self, model, method, args, kwargs):
        res = self._call_kw(model, method, args, kwargs)
        context = kwargs.get("context")
        if context and context.get("extended_name_with_contact"):
            res = self._extend_name(model, res)
        return res
