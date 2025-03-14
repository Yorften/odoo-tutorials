from odoo import _, api, fields, models


class GitlabProjectMember(models.Model):
    _name = "gitlab.member"
    _description = "Gitlab project members"

    name = fields.Char("Name")
