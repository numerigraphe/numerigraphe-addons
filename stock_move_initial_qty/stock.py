# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import osv, fields
import decimal_precision as dp

class stock_move(osv.osv):
    """Keep track of the initial quantity of product."""
    _inherit = 'stock.move'

    def action_confirm(self, cr, uid, ids, context=None):
        """Keep track of the quantity of product when the move is confirmed."""
        for move in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, move.id,
                     {'product_initial_qty': move.product_qty}, context=context)
        return super(stock_move, self).action_confirm(cr, uid, ids,
                                                      context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default and default.copy() or {}
        default['product_initial_qty']=0
        return super(stock_move, self).copy(cr, uid, id, default=default,
                                            context=context)
        
    _columns = {
                'product_initial_qty': fields.float('Initial quantity',
                    digits_compute=dp.get_precision('Product UoM'),
                    help='This is the quantity of product initially intended '
                         'for this Stock Move.'),
    }
stock_move()
