from odoo import models, fields


class OdooVerison(models.Model):
    _name = "odoo.version"
    _description = "Odoo version tags"

    name = fields.Char(string="Version", required=True)
    color = fields.Char(
        string="Color Index",
        default=lambda self: self._default_color(),
        help="Tag color. No color means no display in kanban or front-end, to distinguish internal tags from public categorization tags.",
    )
    _order = "name"

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "A name with the same name already exists.",
        )
    ]

    def _default_color(self):
        return "#FFFFFF"
