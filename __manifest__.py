# -*- coding: utf-8 -*-

{

    'name': 'Fleet Auction',
    'version': '17.0.1.0.0',
    'summary': 'Fleet auction',
    'author' :'sreenath',
    'website': 'https://www.cybrosys.com',
    'maintainer': 'sreenath',
    'description':'Fleet Auction Module',
    'category':'Fleet Auction',
    'data': [
        'security/fleet_auction_user_groups.xml',
        'security/fleet_auction_company_access_security.xml',
        'security/fleet_auction_security.xml',
        'security/ir.model.access.csv',
        'data/fleet_auction_sequence.xml',
        'data/invoice_posting_email.xml',
        'data/auction_scheduled_actions.xml',
        'data/auction_congratulations_email.xml',
        'views/fleet_auction_views.xml',
        'views/auction_bid_views.xml',
        'views/vehicle_views.xml',
        'wizard/auction_canceled_wizard.xml'


    ],
    'depends': [
        'base',
        'fleet',
        'mail',
        'crm',
        'product',
        'account'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
