from odoo import models, fields, api, _
from odoo.tools.date_utils import relativedelta
from odoo.exceptions import UserError

from lxml import etree
import json
import logging

_logger = logging.getLogger(__name__)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property model"

    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("recieved", "Offer Recieved"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        readonly=True,
        required=True,
        copy=False,
        default="new",
        compute="_compute_property_state",
        store=True,
    )

    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id)

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Date Availability", copy=False, default=fields.Date.today() + relativedelta(days=7))
    expected_price = fields.Monetary(string="Expected Price", required=True, currency_field="currency_id")
    selling_price = fields.Monetary(string="Selling Price", readonly=True, copy=False, currency_field="currency_id")
    bedrooms = fields.Integer(string="Bed Rooms", default=2)
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        string="Garden Orientation",
    )
    total_area = fields.Float(string="Total Area", compute="_compute_total_area")
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")

    # RELATIONAL FIELDS

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )

    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.garden_area + property.living_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for property in self:
            property.best_offer = max(property.offer_ids.mapped("price")) if property.offer_ids else 0

    @api.depends("offer_ids")
    def _compute_property_state(self):
        for property in self:
            if not property.offer_ids:
                self.state = "new"

    @api.onchange("garden")
    def _onchange_garden(self):
        for property in self:
            if not property.garden:
                property.garden_area = 0
                property.garden_orientation = ""

    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        for property in self:
            if property.date_availability:
                if property.date_availability < fields.Date.today():
                    return {
                        "warning": {
                            "title": _("Warning"),
                            "message": _("Availability shouldn't be in the past"),
                        }
                    }

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form":
            for node in arch.xpath("//field"):
                field_name = node.get("name")
                field = self._fields.get(field_name)

                # Get xml readonly attribute
                readonly_modifier = node.attrib.get("readonly")

                # Check model field readonly attribute
                if field and field.readonly:
                    continue

                readonly_condition = "state == 'canceled' or state == 'sold'"

                if node.xpath("ancestor::list"):
                    readonly_condition = "property_id.state == 'canceled' or property_id.state == 'sold'"

                if readonly_modifier:
                    readonly_condition += " or " + readonly_modifier

                node.set("readonly", readonly_condition)
        return arch, view

    def action_sold(self):
        self.ensure_one()
        if not self.offer_ids:
            raise UserError(_("An offer is already accepted for this porperty"))
        else:
            self.state = "sold"

    def action_cancel(self):
        if self.state == "accepted":
            raise UserError(_("An offer is already accepted for this porperty"))
        self.ensure_one()
        self.state = "canceled"

    def action_undo(self):
        self.ensure_one()
        statuses = self.offer_ids.mapped("status")

        if "accepted" in statuses:
            self.state = "accepted"
        elif statuses:
            self.state = "recieved"
        else:
            self.state = "new"
