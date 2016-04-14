# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL.
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


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    lock_reason = fields.Selection(
        selection_add=[('first', "Product in the state 'First Use'.")])

    def _get_lock_reason(self, product):
        """Lock new lots when the product is in "First Use" state"""
        reason = super(StockProductionLot, self)._get_lock_reason(product)
        if (product.state == 'first' and product.categ_id.lot_firstuse_locked):
            reason = 'first'
        return reason
