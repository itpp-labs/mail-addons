# -*- coding: utf-8 -*-
{
    "name": """Partner mails count""",
    "summary": """Displays amount of incoming and outgoing partner mails.""",
    "category": "Discuss",
    "images": ['images/1.png'],
    "version": "1.0.0",

    "author": "IT-Projects LLC",
    "website": "https://it-projects.info",
    "license": "GPL-3",

    "depends": [
        'base',
        'mail',
        'web_tour_extra',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/res_partner_mails_count.xml',
        'templates.xml',
    ],
    "demo": [
    ],
    "installable": True,
    "auto_install": False,
}
