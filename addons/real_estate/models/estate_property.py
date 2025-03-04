from odoo import models, fields, api
from odoo.tools.date_utils import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property model"

    def _default_date(self):
        return fields.Date.add(fields.Date.today(), relativedelta(months=+3))

    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("recieved", "Offer Recieved"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Date Availability", copy=False, default=_default_date)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bed Rooms", default=2)
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection(
        [
            ("none", ""),
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

    @api.onchange("garden")
    def _onchange_garden(self):
        for estate in self:
            if not estate.garden:
                estate.garden_area = 0
