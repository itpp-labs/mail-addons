# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License MIT (https://opensource.org/licenses/MIT).
{
    "name": """Multi-Brand Mailing""",
    "summary": """Use single Backend to manage several Websites""",
    "category": "Discuss",
    "images": ["images/main.jpg"],
    "version": "11.0.1.0.1",
    "application": False,
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@itpp.dev",
    "website": "https://twitter.com/OdooFree",
    "license": "Other OSI approved licence",  # MIT
    "price": 230.00,
    "currency": "EUR",
    "depends": ["ir_config_parameter_multi_company", "web_website", "mail"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views/website_views.xml"],
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "auto_install": False,
    "installable": True,
}
