from odoo import _, api, fields, models


class GitlabProjectMember(models.Model):
    _name = "gitlab.member"
    _description = "Gitlab project members"

    member_id = fields.Integer("Id")
    name = fields.Char("Name")

    _sql_constraints = [
        (
            "unique_member_id",
            "unique(member_id)",
            "A Member with the same id already exists.",
        )
    ]