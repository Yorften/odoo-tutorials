from odoo import models, fields
from odoo.tools.date_utils import relativedelta


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Tags of Estate Property Model"

    name = fields.Char(string="Name", required=True)