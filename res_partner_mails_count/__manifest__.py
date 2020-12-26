# -*- coding: utf-8 -*-
{
    "name": """Partner mails count""",
    "summary": """Displays amount of incoming and outgoing partner mails.""",
    "category": "Discuss",
    "images": ["images/1.png"],
    "vesion": "10.0.1.0.0",
    "author": "IT-Projects LLC, Pavel Romanchenko",
    "support": "apps@itpp.dev",
    "website": "https://it-projects.info",
    "license": "Other OSI approved licence",  # MIT
    "depends": [
        "mail_all",
        # 'web_tour_extra',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views/res_partner_mails_count.xml", "templates.xml"],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
