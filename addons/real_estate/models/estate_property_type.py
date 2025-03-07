from odoo import models, fields
from odoo.tools.date_utils import relativedelta


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Types of Estate Property Model"

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "A type with the same name already exists.",
        )
    ]
