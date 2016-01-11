# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_locked_lots = fields.Boolean(
        string='Allow to move blocked Serial Numbers',
        help="Checking this indicates that this location is used as part of "
             "the reception of goods, and it is acceptable to move "
             "Serial Numbers to this location even when they are blocked.")
