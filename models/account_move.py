# -*- coding: utf-8 -*-

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """send email to customer when the invoice is confirmed"""
        res = super().action_post()
        if self.state == 'posted':
            mail_template = (
                self.env.ref('fleet_auction.invoice_posting_email_template'))
            mail_template.send_mail(self.id, force_send=True)
        return res
