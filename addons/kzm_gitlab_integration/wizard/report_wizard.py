from odoo import models, fields, api
import base64
import io
import csv


class ReportWizard(models.TransientModel):
    _name = "report.wizard"
    _description = "Report Wizard"

    report_type = fields.Selection([("pdf", "PDF"), ("csv", "CSV")], string="Report Type", required=True, default="pdf")

    def action_download_report(self):
        active_id = self.env.context.get("active_id")
        project = self.env["gitlab.project"].browse(active_id)
        if self.report_type == "pdf":
            return self.env.ref("kzm_gitlab_integration.gitlab_project_report_action").report_action(project)
        elif self.report_type == "csv":
            url = "/report/download/%s" % active_id

            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }
