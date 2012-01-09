# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
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

"""Compute the net weight of sale orders."""

from osv import osv, fields
class sale_order(osv.osv):
    """Add the total net weight to the object "Sale Order"."""

    _inherit = "sale.order"

    def _total_weight_net(self, cr, uid, ids, field_name, arg, context=None):
        """Compute the total net weight of the given Sale Orders."""
        result = {}
        for sale in self.browse(cr, uid, ids, context=context):
            result[sale.id] = 0.0
            for line in sale.order_line:
                if line.product_id:
                    result[sale.id] += (line.product_id.weight_net
                     * line.product_uom_qty / line.product_uom.factor)
        return result

    def _get_order(self, cr, uid, ids, context=None):
        """Get the order ids of the given Sale Order Lines."""
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids,
            context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'total_weight_net': fields.function(_total_weight_net, method=True,
            readonly=True, string='Total Net Weight',
            help="The cumulated net weight of all the order lines.",
            store={
                # Low priority to compute this before fields in other modules
                'sale.order': (lambda self, cr, uid, ids, context=None: ids,
                     ['order_line'], -10),
                'sale.order.line': (_get_order,
                     ['product_uom_qty', 'product_uom','product_id'], -10),
            },
        ),
    }
sale_order()

class sale_order_line(osv.osv):
    """Add the net weight to the object "Sale Order Line"."""
    
    _inherit = 'sale.order.line'

    def _weight_net(self, cr, uid, ids, field_name, arg, context=None):
        """Compute the net weight of the given Sale Order Lines."""
        result = {}
        uom_obj = self.pool.get('product.uom')
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = 0.0
            if line.product_id and line.product_id.weight > 0.00:
                qty = line.product_uom_qty
                # Convert the qty to the right unit of measure
                if line.product_uom.id <> line.product_id.uom_id.id:
                    qty = uom_obj._compute_qty(cr, uid, line.product_uom.id,
                                               line.product_uom_qty,
                                               line.product_id.uom_id.id)
                result[line.id] += qty
        return result

    _columns = {
        'weight_net': fields.function(_weight_net, method=True,
            readonly=True, string='Net Weight', help="The net weight in Kg.",
            store={
                # Low priority to compute this before fields in other modules
               'sale.order.line': (lambda self, cr, uid, ids, context=None: ids,
                   ['product_uom_qty', 'product_uom', 'product_id'], -11),
            },
        ),
    }
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
