# -*- coding: utf-8 -*-
{
    'name': 'Check mail immediately',
    'version': '1.0.1',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    "category": "Discuss",
    'website': 'https://twitter.com/yelizariev',
    'depends': ['base', 'web', 'fetchmail', 'mail'],
    'data': [
        'views.xml',
    ],
    'qweb': [
        "static/src/xml/main.xml",
    ],
    'installable': False
}
