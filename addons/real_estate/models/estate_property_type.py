from odoo import models, fields
from odoo.tools.date_utils import relativedelta


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Types of Estate Property Model"

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
