from odoo import _, api, fields, models
from ..service import GitlabClient
from gitlab.base import RESTObject, RESTObjectList
from typing import List

from pprint import pformat
import logging

_logger = logging.getLogger(__name__)


class GitlabProject(models.Model):
    _name = "gitlab.project"
    _description = "Gitlab projects database"

    project_id = fields.Integer("Id")
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

    _sql_constraints = [
        (
            "unique_project_id",
            "unique(project_id)",
            "A Project with the same id already exists.",
        )
    ]

    # Relational Fields
    odoo_version_id = fields.Many2one("odoo.version", string="Version")
    project_members_ids = fields.Many2many("gitlab.member", string="Project Members")

    def get_active_credentials(self):
        active_credential = self.env["gitlab.credential"].search([("active_token", "=", True)], limit=1)
        return active_credential.access_token if active_credential else None

    def action_sync_project(self):
        _logger.info("Project names: %s", self.project_name)
        token = self.get_active_credentials()
        if not token:
            _logger.warning("No active GitLab credential found.")
            return
        client = GitlabClient._get_gitlab_client(token)
        project = client.projects.get(self.project_name)
        project_branches = len(project.branches.list())
        project_members = project.members.list()
        self.project_id = project.attributes.get("id")
        self.name = project.attributes.get("name")
        self.description = project.attributes.get("description")
        self.link = project.attributes.get("web_url")
        self.git_link = project.attributes.get("http_url_to_repo")
        self.branches = project_branches
        self.default_branch = project.attributes.get("default_branch")
        self.group = project.attributes.get("namespace").get("kind")
        self.sync_project_members(project_members)
        # self.last_merge = project.attributes.get()

        # _logger.info("Project branches %d", project_branches)
        _logger.info("Project merge reauests %s", pformat([req.attributes for req in project.mergerequests.list()]))
        return True

    def sync_project_members(self, gitlab_members: RESTObjectList | List[RESTObject]):
        MemberModel = self.env["gitlab.member"]
        member_ids = []
        for member in gitlab_members:
            member_id = member.attributes.get("id")
            existing_member = MemberModel.search([("member_id", "=", member_id)], limit=1)
            if not existing_member:
                existing_member = MemberModel.create(
                    {
                        "member_id": member_id,
                        "name": member.attributes.get("name"),
                    }
                )
            member_ids.append(existing_member.id)

        self.write({"project_members_ids": [(6, 0, member_ids)]})
