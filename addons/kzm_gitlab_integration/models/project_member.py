from odoo import _, api, fields, models


class ProjectDatabase(models.Model):
    _name = "project.member"
    _description = "Gitlab project members"

    name = fields.Char('Name')
