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

# noinspection PyStatementEffect
{
    "name": "Robust Mails",
    "version": "13.0.1.2.0",
    "license": "AGPL-3",
    "summary": """
    Adds fields on outgoing email server that allows you to better control the
    outgoing email headers and Reply-To addresses.
    """,
    "data": ["data/ir_config_parameter_data.xml", "views/ir_mail_server_views.xml"],
    "author": "Avoin.Systems",
    "website": "https://avoin.systems",
    "category": "Email",
    "depends": ["mail"],
    "external_dependencies": {
        "python": ["Crypto.Cipher.AES"],  # pip3 install pycryptodome
        "bin": [],
    },
    "installable": True,
    "post_init_hook": "set_catchall_alias",
}
