from odoo import _, api, fields, models


class OdooVerison(models.Model):
    _name = "odoo.version"
    _description = "Odoo version tags"
    _order = "sequence"
    
    version = fields.Char(string="Version", required=True)
    color = fields.Char(string="Color")
    _order = "version"

    _sql_constraints = [
        (
            "unique_version",
            "unique(version)",
            "A version with the same name already exists.",
        )
    ]

    # Relational Fields
    project_ids = fields.One2many('project.database', 'odoo_version_id')