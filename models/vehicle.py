from odoo import fields, models


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    current_value = fields.Monetary(string="Current Value")
    vehicle_id = fields.Many2one('fleet.auction')

    def action_create_auction(self):
        """button within Fleet to create an auction from the Fleet form view"""
        self.vehicle_id = (self.env['fleet.auction'].
                           create({'vehicle_id': self.id}).id)

    def action_view_auction(self):
        """smart button for auction that created from fleet form"""
        return {
            'name': 'FleetAuction',
            'view_mode': 'form',
            'res_model': 'fleet.auction',
            'type': 'ir.actions.act_window',
            'res_id': self.vehicle_id.id
        }
