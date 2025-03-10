from odoo import models, fields, api, _
from odoo.tools.date_utils import relativedelta
from odoo.exceptions import UserError

from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Offers of Estate Property Model"
    _order = "price desc"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Date Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    property_state = fields.Selection(related="property_id.state", store=True, string="Property State")

    _sql_constraints = [
        ("price_positive", "check(price > 0)", "Price must be positive"),
    ]

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            base_date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = base_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            base_date = offer.create_date.date() if offer.create_date else fields.Date.today()
            if offer.date_deadline:
                difference = (offer.date_deadline - base_date).days
                offer.validity = max(difference, 0)
            else:
                offer.validity = 0

    def action_accept(self):
        self.ensure_one()
        if "accepted" in self.property_id.offer_ids.mapped("status"):
            raise UserError(_("An offer is already accepted for this porperty"))
        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.state = "accepted"
        self.property_id.buyer_id = self.partner_id

    def action_refuse(self):
        self.ensure_one()
        if self.status == "accepted":
            raise UserError(_("You can't refuse an already accepted for this porperty"))
        self.status = "refused"

    def action_undo(self):
        self.ensure_one()
        self.property_id.selling_price = 0
        self.property_id.state = "recieved"
        self.property_id.buyer_id = False
        return self.with_context(bypass_status_check=True).write({"status": ""})

    def _check_property_state(self, val):
        _logger.info("offer value : %s", val)
        property_id = val.get("property_id")
        if property_id:
            property_obj = self.env["estate.property"].browse(property_id)
            property_obj.write({"state": "recieved"})

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Creating offer with vals: %s", vals_list)
        for val in vals_list:
            self._check_property_state(val)

        offers = super().create(vals_list)

        manager_group = self.env.ref("real_estate.estate_group_manager")
        manager = self.env["res.users"].search([("groups_id", "in", manager_group.ids)], limit=1)

        for offer in offers:
            salesperson = offer.property_id.salesperson_id
            if salesperson:
                offer.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Follow up on new offer listing"),
                    user_id=salesperson.id,
                    date_deadline=fields.Date.context_today(offer) + relativedelta(days=3),
                )
                _logger.info("Activity scheduled for agent successfully")
            else:
                _logger.warning("No salesperson assigned for property %s", offer.property_id)

            if manager:
                offer.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Manager follow up on new offer listing"),
                    user_id=manager.id,
                    date_deadline=fields.Date.context_today(offer) + relativedelta(days=3),
                )
                _logger.info("Activity scheduled for manager successfully")
            else:
                _logger.warning("No manager found to notify for offer %s", offer.id)

        return offers

    def write(self, vals):
        self.ensure_one()
        # _logger.info("Writing offer %s with context: %s", self.id, self.env.context.get("bypass_status_check"))
        if self.status == "accepted" and not self.env.context.get("bypass_status_check"):
            raise UserError(_("You cannot update an accepted offer."))
        if "status" not in vals:
            vals["status"] = ""
        return super(EstatePropertyOffer, self).write(vals)

    def unlink(self):
        for offer in self:
            if offer.status == "accepted":
                raise UserError(_("You cannot delete an accepted offer."))
            return super(EstatePropertyOffer, self).unlink()


    def cron_auto_confirm_best_offer(self):
        today = date.today()
        expired_properties = self.env["estate.property"].search(
            [("date_deadline", "<=", today), ("state", "=", "recieved"), ("offer_ids", "!=", False)]
        )
        for property in expired_properties:
            best_offer = property.offer_ids.filtered(lambda o: o.status != "refused").sorted("price", reverse=True)[:1]
            best_offer.action_accept()
