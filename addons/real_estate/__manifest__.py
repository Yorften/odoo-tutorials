# -*- coding: utf-8 -*-
{
    "name": "Real Estate",
    "summary": """
        Module summary
    """,
    "description": """
        module Description
    """,
    "author": "Badi",
    "website": "https://www.odoo.com",
    "category": "Real Estate/Porperty",
    "version": "0.1",
    "sequence": 1,
    "application": True,
    "installable": True,
    "depends": ["base", "base_setup", "mail", "contacts"],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
        "views/estate_property_type_views.xml",
        "views/estate_property_offer_views.xml",
        "views/estate_property_tag_views.xml",
        "views/user_views.xml",
        "views/estate_menu.xml",
        "data/cron.xml",
        "data/mail_template_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "real_estate/static/src/js/estate_offer_widget.js",
        ],
    },
    "demo": ["demo/demo.xml"],
    "license": "AGPL-3",
}
