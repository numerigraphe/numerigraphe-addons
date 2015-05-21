# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2015 Numérigraphe SARL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allow_locked_lots = fields.Boolean(
        string='Allow to move blocked Serial Numbers',
        help="Checking this indicates that this location is used as part of "
             "the reception of goods, and it is acceptable to move "
             "Serial Numbers to this location even when they are blocked.")
