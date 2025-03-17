import io
import csv
from odoo import http
from odoo.http import request


class ReportDownloadController(http.Controller):
    @http.route("/report/download/<int:project_id>", type="http", auth="user", website=False)
    def download_csv(self, project_id, **kwargs):

        project = request.env["gitlab.project"].browse(project_id)
        if not project.exists():
            return request.not_found()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Project ID",
                "Name",
                "Project Name",
                "Link",
                "Git Link",
                "Position",
                "Branches",
                "Group",
                "Description",
                "Default Branch",
                "Pipeline Status",
                "Code Score",
                "Last Merge Request",
            ]
        )
        writer.writerow(
            [
                project.project_id,
                project.name,
                project.project_name,
                project.link,
                project.git_link,
                project.position,
                project.branches,
                project.group,
                project.description,
                project.default_branch,
                project.pipeline_status,
                project.code_score,
                project.last_merge,
            ]
        )
        csv_data = output.getvalue()
        output.close()

        headers = [("Content-Type", "text/csv"), ("Content-Disposition", 'attachment; filename="project_report.csv"')]
        return request.make_response(csv_data, headers=headers)
