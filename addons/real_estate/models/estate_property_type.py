from odoo import models, fields, api, _
from odoo.tools.date_utils import relativedelta


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Types of Estate Property Model"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    sequence = fields.Integer("Sequence", default=1, help="Used to order types. Lower is better.")
    offer_count = fields.Integer(compute="_compute_total_offers")

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "A type with the same name already exists.",
        )
    ]

    @api.depends("offer_ids")
    def _compute_total_offers(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)
