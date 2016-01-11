# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Allow users to move locked lots in receipt locations',
    'version': '1.0',
    'author': u'Numérigraphe',
    "category": "Warehouse Management",
    'description': """
Normally locked lots can't be selected in pickings. This module lets you
define receipt locations to which locked lots can be moved.

This allows stock workers to put away the received goods within certain
limits.
    """,
    'depends': [
        'stock_lock_lot',
    ],
    'data': [
        'views/stock_location_view.xml',
        'wizard/stock_transfer_details_view.xml',
    ],
    'license': 'AGPL-3',
}
