{
    "name": "Sentbox",
    "summary": """Quick way to find sent messages""",
    "category": "Discuss",
    "images": ['images/menu.png'],
    "version": "11.0.1.0.4",

    "author": "IT-Projects LLC, Ivan Yelizariev, Pavel Romanchenko",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info",
    "license": "LGPL-3",
    'price': 40.00,
    'currency': 'EUR',

    "depends": [
        "base",
        "mail",
        "mail_base"
    ],

    "data": [
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/menu.xml",
    ],
    'installable': True,
}
