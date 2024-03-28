# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Bid(models.Model):
    _name = "auction.bid"
    _description = "Auction Bid"
    _inherit = 'mail.thread'

    auction_id = fields.Many2one("fleet.auction", string='Auction',
                                 help='auction id here', ondelete='cascade',
                                 required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company.id,
                                 string="Company", help="Company")
    currency_id = fields.Many2one('res.currency',
                                  default=lambda
                                  self: self.company_id.currency_id.id,
                                  string="Currency",
                                  help="Currency")
    bid_amount = fields.Float(string='Bid Amount', help='Bid amount here')
    bid_price = fields.Float(string='Bid Price', help='bid price here')
    bid_date = fields.Date(help="Choose the start date", string="Bid Date")
    phone_number = fields.Char(string='Phone Number',
                               help='enter the phone number here')
    state = fields.Selection([("draft", "Draft"),
                              ("confirmed", "Confirmed")],
                             tracking=True, default="draft")
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 help="Choose the customer", required=True)

    def action_confirm_bid(self):
        """to change the state into confirmed"""
        self.state = 'confirmed'

    @api.constrains('auction_id', 'bid_price', 'bid_amount')
    def bid_price_constrains(self):
        """validation for bid price and bid amount"""
        for rec in self:
            if rec.bid_price == 0 or rec.bid_amount == 0:
                raise ValidationError(
                    'Error,Bid price and Bid Amount should be greater than'
                    ' zero')
