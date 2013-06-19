# -*- coding: utf-8 -*-
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
from tools.translate import _

class stock_inventory_valuation(osv.osv):
    """ Save products informations (quantity, standard price) when inventory is confirmed.
    """
    _name = 'stock.inventory.valuation'
    _description = 'Stock inventory valuation'

    _columns = {
        'name': fields.char('name', size=64, required=True, select=True),
        'inventory_id': fields.many2one('stock.inventory', 'Inventory', ondelete='cascade', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='restrict', readonly=True),
        'product_qty': fields.float('Inventory Quantity', digits_compute=dp.get_precision('Product UoM')),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True, help="unit of measure of product."),
        'standard_price': fields.float('Cost Price', required=True, digits_compute=dp.get_precision('Product Price'), help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
    }

stock_inventory_valuation()

class stock_inventory(osv.osv):
    """ This class make link between stock_inventory object and stock_inventory_valuation object """
    _inherit = 'stock.inventory'
    _columns = {
        'valuation_ids': fields.one2many('stock.inventory.valuation', 'inventory_id', 'Product Valuations',
                                         ondelete='cascade', readonly=True)
    }

    def inventory_lines(self, inventory):
        """Generator of inventory line Ids.
        
        This default implementation is trivial, but this method exists for
        inherited models to redefine it, to include other inventory lines."""
        for line in inventory.inventory_line_id:
            yield line

    def action_confirm(self, cr, uid, ids, context=None):
        """ Compute the valuation of products. 
        
        @param context['valuation']: enable/disable the computation of the valuation 
        """
        if context is None:
            context = {}
        
        if context.get('valuation', True):
            for inv in self.browse(cr, uid, ids, context=context):
                # Collect the valuation of each product
                values = {}
                for line in self.inventory_lines(inv):
                    if line.product_id.id in values:
                        value = values[line.product_id.id]
                        value['product_qty'] += line.product_qty
                    else:
                        value = {
                            'name': 'INV:' + str(inv.id) + ':' + inv.name,
                            'inventory_id': inv.id,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom.id,
                            'product_qty': line.product_qty,
                            'standard_price': line.product_id.standard_price,
                            }
                    values[line.product_id.id] = value
                
                # Record the valuations
                for value in values.itervalues():
                    self.pool.get('stock.inventory.valuation').create(cr, uid, value, context=context)

                message = _("Product valuation for '%s' is done") % inv.name
                self.log(cr, uid, inv.id, message)
        return super(stock_inventory, self).action_confirm(cr, uid, ids, context=context)

    def action_cancel_inventary(self, cr, uid, ids, context=None):
        """ to delete records valuation on database.
        """
        siv_obj = self.pool.get('stock.inventory.valuation')
        for inv in self.browse(cr, uid, ids, context=context):
            siv_line_ids = siv_obj.search(cr, uid, [('inventory_id', '=', inv.id)])
            siv_obj.unlink(cr, uid, siv_line_ids, context=context)
        return super(stock_inventory, self).action_cancel_inventary(cr, uid, ids, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        """Do not copy the product valuation when cloning inventories"""
        default = default and default.copy() or {}
        default['valuation_ids'] = []
        return super(stock_inventory, self).copy(cr, uid, id, default=default, context=context)
    
stock_inventory()

