from odoo import _, api, fields, models
from ..tools import FernetUtils
from ..service import GitlabClient
from gitlab.exceptions import GitlabAuthenticationError

from pprint import pformat
import logging

_logger = logging.getLogger(__name__)


class GitlabCredential(models.Model):
    _name = "gitlab.credential"
    _description = "Gitlab credentials for private repositories"

    token_name = fields.Char("Token Name")
    access_token = fields.Char("Access Token")
    active_token = fields.Boolean("Active Token", default=False)
    state = fields.Selection([("active", "Active"), ("inactive", "Inactive")], string="Status", default="inactive")
    _sql_constraints = [
        (
            "unique_token_name",
            "unique(token_name)",
            "A token with the same name already exists.",
        )
    ]

    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.uid, readonly=True)

    def get_active_credentials(self):
        active_credential = self.env["gitlab.credential"].search([("active_token", "=", True)], limit=1)
        return active_credential.access_token if active_credential else None

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Encrypting the token first
            if "access_token" in vals:
                vals["access_token"] = FernetUtils.get_fernet().encrypt(self.encode_token(vals["access_token"]))
                _logger.info("Encrypted token: %s", vals["access_token"])
        records = super(GitlabCredential, self).create(vals_list)
        for record in records:
            if record.active_token:
                record._deactivate_other_tokens()
        return records

    def write(self, vals):
        # Encrypting the token first
        if "access_token" in vals and vals["access_token"]:
            vals["access_token"] = FernetUtils.get_fernet().encrypt(self.encode_token(vals["access_token"]))
            _logger.info("Encrypted token: %s", vals["access_token"])
        res = super(GitlabCredential, self).write(vals)
        if "active_token" in vals:
            self._deactivate_other_tokens()

        return res

    def action_verify_credentials(self):
        return True

    def _deactivate_other_tokens(self):
        """
        For each record in self marked as active,
        set active=False and state='inactive' on all other tokens for the same user.
        """
        for rec in self:
            other_tokens = self.search([("user_id", "=", rec.user_id.id), ("id", "!=", rec.id), ("active_token", "=", True)])
            if other_tokens:
                other_tokens.write({"active_token": False, "state": "inactive"})

    def action_verify_credentials(self):
        self.ensure_one()
        try:
            GitlabClient._get_gitlab_client(self.access_token)
            self.state = "active"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Verification success"),
                    "type": "success",
                    "message": _("Authentication succeed!"),
                    "sticky": True,
                },
            }
        except GitlabAuthenticationError as e:
            self.state = "inactive"
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Authentication failed"),
                    "type": "error",
                    "message": _("Authentication failed: %s", e.error_message),
                    "sticky": True,
                },
            }

    def encode_token(self, token):
        if isinstance(token, str):
            return token.encode("utf-8")
