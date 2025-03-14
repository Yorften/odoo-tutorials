from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Tags of Estate Property Model"

    name = fields.Char(string="Name", required=True)
    color = fields.Char(string="Color")
    _order = "name"

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "A tag with the same name already exists.",
        )
    ]
