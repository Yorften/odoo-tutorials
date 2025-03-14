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
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/gitlab_credential_views.xml",
        "views/project_database_views.xml",
        "views/project_member_views.xml",
        "views/odoo_version_views.xml",
        "views/gitlab_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "external_dependencies": {
        "python": ["gitlab"],
    },
    "demo": [],
    "license": "AGPL-3",
}
