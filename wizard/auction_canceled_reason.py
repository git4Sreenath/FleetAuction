# -*- coding: utf-8 -*-

from odoo import fields, models


class AuctionCanceledWizard(models.TransientModel):
    _name = "auction.canceled.wizard"
    _description = "Auction Canceled Reason"

    cancel_reason = fields.Char(string='closed reason', required=True)

    def cancel_reason_from_wizard(self):
        auction = self.env['fleet.auction'].browse(
            self.env.context.get('active_id'))
        auction.state = 'cancelled'
