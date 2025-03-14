from odoo import _, api, fields, models
from ..service import GitlabClient

from pprint import pformat
import logging

_logger = logging.getLogger(__name__)


class GitlabProject(models.Model):
    _name = "gitlab.project"
    _description = "Gitlab projects database"

    id = fields.Integer("Id")
    name = fields.Char("Name")
    link = fields.Char("Link")
    git_link = fields.Char("Git Link")
    position = fields.Selection(
        [("test", "TEST"), ("pre_prod", "PRE PROD"), ("prod", "PROD")], string="Position", default="test"
    )
    branches = fields.Integer("Branches")
    group = fields.Char("Group")
    project_name = fields.Char("Project Name", required=True)
    description = fields.Char("Description")
    default_branch = fields.Char("Default Branch")
    pipeline_status = fields.Selection([("success", "Succeed"), ("fail", "Failed")], string="Pipeline Status")
    code_score = fields.Float("Code Score")
    last_merge = fields.Char("Last Merge request")

    # Relational Fields
    odoo_version_id = fields.Many2one("odoo.version", string="Version")
    project_members_ids = fields.Many2many("gitlab.member", string="Project Members")

    def get_active_credentials(self):
        active_credential = self.env["gitlab.credential"].search([("active_token", "=", True)], limit=1)
        return active_credential.access_token if active_credential else None

    # def _sync_project_with_gitlab(self):
    #     token = self.get_active_credentials()
    #     if not token:
    #         _logger.warning("No active GitLab credential found.")
    #         return

    #     try:
    #         _logger.info("token %s", token)
    #         client = GitlabClient._get_gitlab_client(token)
    #         current_user = client.user
    #         user = client.users.get(current_user.id)
    #         projects = user.projects.list(iterator=True)
    #         # _logger.info("Project names: %s", pformat([project.attributes for project in projects]))
    #         _logger.info("Project names: %s", projects)

    #         for project in projects:
    #             git_link = project.attributes.get("http_url_to_repo")  # git link
    #             existing = self.search([("git_link", "=", git_link)], limit=1)
    #             project_branches = len(client.projects.get(project.attributes.get("id")).branches.list())
    #             _logger.info("Project names: %s", project.attributes)
    #             _logger.info("Project branches %d", project_branches)
    #             vals = {
    #                 "id": project.attributes.get("id"),
    #                 "name": project.attributes.get("name"),
    #                 "description": project.attributes.get("description") or "",
    #                 "link": project.attributes.get("web_url") or "",
    #                 "git_link": project.attributes.get("http_url_to_repo") or "",
    #                 "branches": project_branches,
    #                 "default_branch": project.attributes.get("default_branch") or "",
    #                 # "group": project.attributes.get() or "",
    #                 # "default_branch": project.attributes.get() or "",
    #                 # "last_merge": project.attributes.get() or "",
    #             }
    #             if existing:
    #                 existing.write(vals)
    #             else:
    #                 self.create(vals)
    #     except Exception as e:
    #         _logger.exception("Exception while syncing projects from GitLab: %s", e)

    def action_sync_project(self):
        _logger.info("Project names: %s", self.project_name)
        token = self.get_active_credentials()
        if not token:
            _logger.warning("No active GitLab credential found.")
            return
        client = GitlabClient._get_gitlab_client(token)
        project = client.projects.get(self.project_name)
        _logger.info("Project names: %s", pformat(project.attributes))
        return True
