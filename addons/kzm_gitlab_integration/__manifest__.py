# -*- coding: utf-8 -*-
{
    "name": "Gitlab",
    "summary": """
        Gitlab integration in Odoo 18.0
    """,
    "description": """
        Gitlab integration in Odoo 18.0
    """,
    "author": "Badi",
    "website": "https://www.odoo.com",
    "category": "Services/Services",
    "version": "0.1",
    "sequence": 1,
    "application": True,
    "installable": True,
    "depends": ["base", "base_setup"],
    "data": [
        "views/gitlab_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "demo": [],
    "license": "AGPL-3",
}
