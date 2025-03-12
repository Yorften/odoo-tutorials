from odoo import _, api, fields, models


class ProjectDatabase(models.Model):
    _name = "project.database"
    _description = "Gitlab projects database"

    name = fields.Char("Name")
    link = fields.Char("Link")
    git_link = fields.Char("Git Link")
    position = fields.Selection([("test", "TEST"), ("pre_prod", "PRE PROD"), ("prod", "PROD")], string="Position")
    branches = fields.Integer("Branches", readonly=True)
    group = fields.Char("Group")
    project_name = fields.Char("Project Name")
    description = fields.Char("Description")
    default_branch = fields.Char("Default Branch")
    pipeline_status = fields.Selection([("success", "Succeed"), ("fail", "Failed")], string="Pipeline Status")
    code_score = fields.Float("Code Score")
    last_merge = fields.Char("Last Merge reauest")

    # Relational Fields
    client_id = fields.Many2one('res.partner', string='Client')
    odoo_version_id = fields.Many2one('odoo.version', string='Version')
    project_members_ids = fields.Many2many('project.member',string='Project Members', readonly=True)