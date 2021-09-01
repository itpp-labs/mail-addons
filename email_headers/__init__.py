##############################################################################
#
#    Author: Avoin.Systems
#    Copyright 2017 Avoin.Systems
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# noinspection PyUnresolvedReferences
from . import models
from odoo import SUPERUSER_ID, api


def set_catchall_alias(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    icp = env["ir.config_parameter"]
    custom_alias = icp.get_param("mail.catchall.alias.custom")
    if not custom_alias:
        original_alias = icp.get_param("mail.catchall.alias", "catchall")
        icp.set_param("mail.catchall.alias.custom", original_alias)
        icp.set_param("mail.catchall.alias", "Use mail.catchall.alias.custom")
