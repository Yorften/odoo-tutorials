from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    credential_ids = fields.One2many("gitlab.credential", "user_id")
