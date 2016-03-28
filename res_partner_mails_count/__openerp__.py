# -*- coding: utf-8 -*-
{
    "name": "Smart buttons for mails count",

    "summary": """
        This module adds Smart buttons with "Mails from" and "Mails to" count of mails in the partner form.
    """,

    "description": """
        You can see Smart buttons "Mails from" and "Mails to" in the contact
        form in the Messaging/Contacts menu. If you click on these buttons,
        you can see list of corresponded mails. Click on the "Send a message"
        link to send mail to the partner.
    """,

    "author": "IT-Projects LLC, Pavel Romanchenko",
    "website": "http://www.it-projects.info",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "1.0.0",

    # any module necessary for this one to work correctly
    "depends": ["base", "mail"],

    # always loaded
    "data": [
        "views/res_partner_mails_count.xml",
        "templates.xml",
    ],
}
