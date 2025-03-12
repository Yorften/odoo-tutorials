from odoo import _, api, fields, models


class GitlabCredential(models.Model):
    _name = "gitlab.credential"
    _description = "Gitlab credentials for private repositories"

    username = fields.Char("Username")
    token = fields.Char("Qccess Token")
