# Copyright 2016 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2016 intero-chz <https://github.com/intero-chz>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, exceptions, fields, models
from odoo.tools import email_split
from odoo.tools.translate import _


class Wizard(models.TransientModel):
    _name = "mail_move_message.wizard"
    _description = "Mail move message wizard"

    @api.model
    def _model_selection(self):
        selection = []
        config_parameters = self.env["ir.config_parameter"]
        model_names = config_parameters.sudo().get_param("mail_relocation_models")
        model_names = model_names.split(",") if model_names else []
        if "default_message_id" in self.env.context:
            message = self.env["mail.message"].browse(
                self.env.context["default_message_id"]
            )
            if message.model and message.model not in model_names:
                model_names.append(message.model)
            if message.moved_from_model and message.moved_from_model not in model_names:
                model_names.append(message.moved_from_model)
        if model_names:
            selection = [
                (m.model, m.display_name)
                for m in self.env["ir.model"].search([("model", "in", model_names)])
            ]
        return selection

    @api.model
    def default_get(self, fields_list):
        res = super(Wizard, self).default_get(fields_list)

        available_models = self._model_selection()
        if len(available_models):
            record = self.env[available_models[0][0]].search([], limit=1)
            res["model_record"] = (
                len(record) and (available_models[0][0] + "," + str(record.id)) or False
            )

        if "message_id" in res:
            message = self.env["mail.message"].browse(res["message_id"])
            email_from = message.email_from
            parts = email_split(email_from.replace(" ", ","))
            if parts:
                email = parts[0]
                name = (
                    email_from.find(email) != -1
                    and email_from[: email_from.index(email)]
                    .replace('"', "")
                    .replace("<", "")
                    .strip()
                    or email_from
                )
            else:
                name, email = email_from
            res["message_name_from"] = name
            res["message_email_from"] = email

            res["partner_id"] = message.author_id.id
            if message.author_id and self.env.uid not in [
                u.id for u in message.author_id.user_ids
            ]:
                res["filter_by_partner"] = True
            if message.author_id and res.get("model"):
                res_id = self.env[res["model"]].search([], order="id desc", limit=1)
                if res_id:
                    res["res_id"] = res_id[0].id

        config_parameters = self.env["ir.config_parameter"]
        res["move_followers"] = config_parameters.sudo().get_param(
            "mail_relocation_move_followers"
        )

        res["uid"] = self.env.uid
        return res

    message_id = fields.Many2one("mail.message", string="Message")
    message_body = fields.Html(
        related="message_id.body", string="Message to move", readonly=True
    )
    message_from = fields.Char(
        related="message_id.email_from", string="From", readonly=True
    )
    message_subject = fields.Char(
        related="message_id.subject", string="Subject", readonly=True
    )
    message_moved_by_message_id = fields.Many2one(
        "mail.message",
        related="message_id.moved_by_message_id",
        string="Moved with",
        readonly=True,
    )
    message_moved_by_user_id = fields.Many2one(
        "res.users",
        related="message_id.moved_by_user_id",
        string="Moved by",
        readonly=True,
    )
    message_is_moved = fields.Boolean(
        string="Is Moved", related="message_id.is_moved", readonly=True
    )
    parent_id = fields.Many2one("mail.message", string="Search by name",)
    model_record = fields.Reference(selection="_model_selection", string="Record")
    model = fields.Char(compute="_compute_model_res_id", string="Model")
    res_id = fields.Integer(compute="_compute_model_res_id", string="Record ID")

    can_move = fields.Boolean("Can move", compute="_compute_get_can_move")
    move_back = fields.Boolean(
        "MOVE TO ORIGIN", help="Move  message and submessages to original place"
    )
    partner_id = fields.Many2one("res.partner", string="Author")
    filter_by_partner = fields.Boolean("Filter Records by partner")
    message_email_from = fields.Char()
    message_name_from = fields.Char()
    # FIXME message_to_read should be True even if current message or any his childs are unread
    message_to_read = fields.Boolean(
        compute="_compute_is_read",
        string="Unread message",
        help="Service field shows that this message were unread when moved",
    )
    uid = fields.Integer()
    move_followers = fields.Boolean(
        "Move Followers",
        help="Add followers of current record to a new record.\n"
        "You must use this option, if new record has restricted access.\n"
        "You can change default value for this option at Settings/System Parameters",
    )

    @api.multi
    @api.depends("model_record")
    def _compute_model_res_id(self):
        for rec in self:
            rec.model = rec.model_record and rec.model_record._name or False
            rec.res_id = rec.model_record and rec.model_record.id or False

    @api.depends("message_id")
    @api.multi
    def _compute_get_can_move(self):
        for r in self:
            r.get_can_move_one()

    @api.multi
    def _compute_is_read(self):
        messages = (
            self.env["mail.message"]
            .sudo()
            .browse(self.message_id.all_child_ids.ids + [self.message_id.id])
        )
        self.message_to_read = True in [m.needaction for m in messages]

    @api.multi
    def get_can_move_one(self):
        self.ensure_one()
        # message was not moved before OR message is a top message of previous move
        self.can_move = (
            not self.message_id.moved_by_message_id
            or self.message_id.moved_by_message_id.id == self.message_id.id
        )

    @api.onchange("move_back")
    def on_change_move_back(self):
        if not self.move_back:
            return
        self.parent_id = self.message_id.moved_from_parent_id
        message = self.message_id
        if message.is_moved:
            self.model_record = self.env[message.moved_from_model].browse(
                message.moved_from_res_id
            )

    @api.onchange("parent_id", "model_record")
    def update_move_back(self):
        model = self.message_id.moved_from_model
        self.move_back = (
            self.parent_id == self.message_id.moved_from_parent_id
            and self.res_id == self.message_id.moved_from_res_id
            and (self.model == model or (not self.model and not model))
        )

    @api.onchange("parent_id")
    def on_change_parent_id(self):
        if self.parent_id and self.parent_id.model:
            self.model = self.parent_id.model
            self.res_id = self.parent_id.res_id
        else:
            self.model = None
            self.res_id = None

    @api.onchange("model", "filter_by_partner", "partner_id")
    def on_change_partner(self):
        domain = {"res_id": [("id", "!=", self.message_id.res_id)]}
        if self.model and self.filter_by_partner and self.partner_id:
            fields = self.env[self.model].fields_get(False)
            contact_field = False
            for n, f in fields.items():
                if f["type"] == "many2one" and f["relation"] == "res.partner":
                    contact_field = n
                    break
            if contact_field:
                domain["res_id"].append((contact_field, "=", self.partner_id.id))
        if self.model:
            res_id = self.env[self.model].search(
                domain["res_id"], order="id desc", limit=1
            )
            self.res_id = res_id and res_id[0].id
        else:
            self.res_id = None
        return {"domain": domain}

    @api.multi
    def check_access(self):
        for r in self:
            r.check_access_one()

    @api.multi
    def check_access_one(self):
        self.ensure_one()
        operation = "write"

        if not (self.model and self.res_id):
            return True
        model_obj = self.env[self.model]
        mids = model_obj.browse(self.res_id).exists()
        if hasattr(model_obj, "check_mail_message_access"):
            model_obj.check_mail_message_access(mids.ids, operation)
        else:
            self.env["mail.thread"].check_mail_message_access(
                mids.ids, operation, model_name=self.model
            )

    @api.multi
    def open_moved_by_message_id(self):
        message_id = None
        for r in self:
            message_id = r.message_moved_by_message_id.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "mail_move_message.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [[False, "form"]],
            "target": "new",
            "context": {"default_message_id": message_id},
        }

    @api.multi
    def move(self):
        for r in self:
            if not r.model:
                raise exceptions.except_orm(
                    _("Record field is empty!"),
                    _("Select a record for relocation first"),
                )
        for r in self:
            r.check_access()
            if not r.parent_id or not (
                r.parent_id.model == r.model and r.parent_id.res_id == r.res_id
            ):
                # link with the first message of record
                parent = self.env["mail.message"].search(
                    [("model", "=", r.model), ("res_id", "=", r.res_id)],
                    order="id",
                    limit=1,
                )
                r.parent_id = parent.id or None
            r.message_id.move(
                r.parent_id.id,
                r.res_id,
                r.model,
                r.move_back,
                r.move_followers,
                r.message_to_read,
                r.partner_id,
            )

        if r.model in ["mail.message", "mail.channel", False]:
            return {
                "name": "Chess game page",
                "type": "ir.actions.act_url",
                "url": "/web",
                "target": "self",
            }
        return {
            "name": _("Record"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": r.model,
            "res_id": r.res_id,
            "views": [(False, "form")],
            "type": "ir.actions.act_window",
        }

    @api.multi
    def delete(self):
        for r in self:
            r.delete_one()

    @api.multi
    def delete_one(self):
        self.ensure_one()
        msg_id = self.message_id.id

        # Send notification
        notification = {"id": msg_id}
        self.env["bus.bus"].sendone(
            (self._cr.dbname, "mail_move_message.delete_message"), notification
        )

        self.message_id.unlink()
        return {}

    @api.multi
    def read_close(self):
        for r in self:
            r.read_close_one()

    @api.multi
    def read_close_one(self):
        self.ensure_one()
        self.message_id.set_message_done()
        self.message_id.child_ids.set_message_done()
        return {"type": "ir.actions.act_window_close"}


class MailMessage(models.Model):
    _inherit = "mail.message"

    is_moved = fields.Boolean("Is moved")
    moved_from_res_id = fields.Integer("Related Document ID (Original)")
    moved_from_model = fields.Char("Related Document Model (Original)")
    moved_from_parent_id = fields.Many2one(
        "mail.message", "Parent Message (Original)", ondelete="set null"
    )
    moved_by_message_id = fields.Many2one(
        "mail.message",
        "Moved by message",
        ondelete="set null",
        help="Top message, that initate moving this message",
    )
    moved_by_user_id = fields.Many2one(
        "res.users", "Moved by user", ondelete="set null"
    )
    all_child_ids = fields.One2many(
        "mail.message",
        string="All childs",
        compute="_compute_get_all_childs",
        help="all childs, including subchilds",
    )
    moved_as_unread = fields.Boolean("Was Unread", default=False)

    @api.multi
    def _compute_get_all_childs(self, include_myself=True):
        for r in self:
            r._get_all_childs_one(include_myself=include_myself)

    @api.multi
    def _get_all_childs_one(self, include_myself=True):
        self.ensure_one()
        ids = []
        if include_myself:
            ids.append(self.id)
        while True:
            new_ids = self.search([("parent_id", "in", ids), ("id", "not in", ids)]).ids
            if new_ids:
                ids = ids + new_ids
                continue
            break
        moved_childs = self.search([("moved_by_message_id", "=", self.id)]).ids
        self.all_child_ids = ids + moved_childs

    @api.multi
    def move_followers(self, model, ids):
        fol_obj = self.env["mail.followers"]
        for message in self:
            followers = fol_obj.sudo().search(
                [("res_model", "=", message.model), ("res_id", "=", message.res_id)]
            )
            for f in followers:
                self.env[model].browse(ids).message_subscribe(
                    [f.partner_id.id], [s.id for s in f.subtype_ids]
                )

    @api.multi
    def move(
        self,
        parent_id,
        res_id,
        model,
        move_back,
        move_followers=False,
        message_to_read=False,
        author=False,
    ):
        for r in self:
            r.move_one(
                parent_id,
                res_id,
                model,
                move_back,
                move_followers=move_followers,
                message_to_read=message_to_read,
                author=author,
            )

    @api.multi
    def move_one(
        self,
        parent_id,
        res_id,
        model,
        move_back,
        move_followers=False,
        message_to_read=False,
        author=False,
    ):
        self.ensure_one()
        if parent_id == self.id:
            # if for any reason method is called to move message with parent
            # equal to oneself, we need stop to prevent infinitive loop in
            # building message tree
            return
        if not self.author_id:
            self.write({"author_id": author.id})

        vals = {}
        if move_back:
            # clear variables if we move everything back
            vals["is_moved"] = False
            vals["moved_by_user_id"] = None
            vals["moved_by_message_id"] = None

            vals["moved_from_res_id"] = None
            vals["moved_from_model"] = None
            vals["moved_from_parent_id"] = None
            vals["moved_as_unread"] = None
        else:
            vals["parent_id"] = parent_id
            vals["res_id"] = res_id
            vals["model"] = model

            vals["is_moved"] = True
            vals["moved_by_user_id"] = self.env.user.id
            vals["moved_by_message_id"] = self.id
            vals["moved_as_unread"] = message_to_read
            # Update record_name in message
            vals["record_name"] = self._get_record_name(vals)

        # unread message remains unread after moving back to origin
        if self.moved_as_unread and move_back:
            notification = {
                "mail_message_id": self.id,
                "res_partner_id": self.env.user.partner_id.id,
                "is_read": False,
            }
            self.write({"notification_ids": [(0, 0, notification)]})

        for r in self.all_child_ids:
            r_vals = vals.copy()
            if not r.is_moved:
                # moved_from_* variables contain not last, but original
                # reference
                r_vals["moved_from_parent_id"] = r.parent_id.id or r.env.context.get(
                    "uid"
                )
                r_vals["moved_from_res_id"] = r.res_id or r.id
                r_vals["moved_from_model"] = r.model or r._name
            elif move_back:
                r_vals["parent_id"] = r.moved_from_parent_id.id
                r_vals["res_id"] = r.moved_from_res_id
                r_vals["model"] = (
                    r.moved_from_model
                    and r.moved_from_model
                    not in ["mail.message", "mail.channel", False]
                ) and r.moved_from_model
                r_vals["record_name"] = (
                    r_vals["model"]
                    and self.env[r.moved_from_model].browse(r.moved_from_res_id).name
                )

            if move_followers:
                r.sudo().move_followers(r_vals.get("model"), r_vals.get("res_id"))
            r.sudo().write(r_vals)
            r.attachment_ids.sudo().write(
                {"res_id": r_vals.get("res_id"), "res_model": r_vals.get("model")}
            )

        # Send notification
        notification = {
            "id": self.id,
            "res_id": vals.get("res_id"),
            "model": vals.get("model"),
            "is_moved": vals["is_moved"],
            "record_name": "record_name" in vals and vals["record_name"],
        }
        self.env["bus.bus"].sendone(
            (self._cr.dbname, "mail_move_message"), notification
        )

    @api.multi
    def name_get(self):
        context = self.env.context
        if not (context or {}).get("extended_name"):
            return super(MailMessage, self).name_get()
        reads = self.read(["record_name", "model", "res_id"])
        res = []
        for record in reads:
            name = record["record_name"] or ""
            extended_name = "   [{}] ID {}".format(
                record.get("model", "UNDEF"), record.get("res_id", "UNDEF"),
            )
            res.append((record["id"], name + extended_name))
        return res

    @api.multi
    def message_format(self):
        message_values = super(MailMessage, self).message_format()
        message_index = {message["id"]: message for message in message_values}
        for item in self:
            msg = message_index.get(item.id)
            if msg:
                msg["is_moved"] = item.is_moved
        return message_values


class MailMoveMessageConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    model_ids = fields.Many2many(comodel_name="ir.model", string="Models")
    move_followers = fields.Boolean("Move Followers")

    @api.model
    def get_values(self):
        res = super(MailMoveMessageConfiguration, self).get_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        model_names = config_parameters.sudo().get_param("mail_relocation_models")
        model_names = model_names.split(",")
        model_ids = self.env["ir.model"].sudo().search([("model", "in", model_names)])
        res.update(
            model_ids=[m.id for m in model_ids],
            move_followers=config_parameters.sudo().get_param(
                "mail_relocation_move_followers"
            ),
        )
        return res

    @api.multi
    def set_values(self):
        super(MailMoveMessageConfiguration, self).set_values()
        config_parameters = self.env["ir.config_parameter"].sudo()
        for record in self:
            model_names = ",".join([x.model for x in record.model_ids])
            config_parameters.set_param("mail_relocation_models", model_names or "")
            config_parameters.set_param(
                "mail_relocation_move_followers", record.move_followers or ""
            )


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if "update_message_author" in self.env.context and "email" in vals:
            mail_message_obj = self.env["mail.message"]
            # Escape special SQL characters in email_address to avoid invalid matches
            email_address = (
                vals["email"]
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            email_brackets = "<%s>" % email_address
            messages = mail_message_obj.search(
                [
                    "|",
                    ("email_from", "=ilike", email_address),
                    ("email_from", "ilike", email_brackets),
                    ("author_id", "=", False),
                ]
            )
            if messages:
                messages.sudo().write({"author_id": res.id})
        return res

    @api.model
    def default_get(self, default_fields):
        contextual_self = self
        if (
            "mail_move_message" in self.env.context
            and self.env.context["mail_move_message"]
        ):
            contextual_self = self.with_context(
                default_name=self.env.context["message_name_from"] or "",
                default_email=self.env.context["message_email_from"] or "",
            )
        return super(ResPartner, contextual_self).default_get(default_fields)
