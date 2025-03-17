from odoo import _, api, fields, models
from ..service import GitlabClient
from gitlab.base import RESTObject, RESTObjectList
from typing import List
from pprint import pformat

import logging
import re

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
    last_merge_url = fields.Char("Last Merge URL")

    last_merge_link = fields.Html(
        string="Last Merge", compute="_compute_last_merge_link", sanitize=False, store=False  # allow HTML markup
    )
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

    @api.depends("last_merge", "last_merge_url")
    def _compute_last_merge_link(self):
        for record in self:
            if record.last_merge and record.last_merge_url:
                record.last_merge_link = f'<a href="{record.last_merge_url}" target="_blank">{record.last_merge}</a>'
            else:
                record.last_merge_link = f'<p target="_blank">None</p>'

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

        # Get the project merge requests
        merge_requests = project.mergerequests.list(order_by="updated_at", sort="desc")
        if merge_requests:
            self.last_merge = merge_requests[0].attributes.get("title")
            self.last_merge_url = merge_requests[0].attributes.get("web_url")
        else:
            self.last_merge = None

        # _logger.info("Project branches %d", project_branches)
        jobs = project.jobs.list(order_by="created_at", sort="desc")
        last_job = jobs[0] if jobs else None

        if last_job:
            if last_job.attributes.get("pipeline").get("status") == "success":
                self.pipeline_status = "success"

                log = project.jobs.get(last_job.attributes.get("id")).artifact("pylint_output.log", streamed=False, iterator=False)
                log_text = log.decode("utf-8")

                m = re.search(r"Your code has been rated at (\d+\.\d+)/10", log_text)
                if m:
                    score = m.group(1)
                    self.code_score = score
                else:
                    _logger.info("Pylint score not found in log")
            else:
                self.pipeline_status = "fail"
        # _logger.info("Project last job %s", last_job.attributes)
        # _logger.info("Project report %s", log_text)

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
