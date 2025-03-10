from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "salesperson_id", domain=[("state", "in", ("new", "recieved"))])
