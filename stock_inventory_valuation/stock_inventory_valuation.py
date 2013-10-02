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

from openerp.osv import osv, fields
import decimal_precision as dp
from openerp.tools.translate import _

class stock_inventory_valuation(osv.osv):
    """Save products informations (quantity, standard price) when inventory is confirmed."""
    _name = 'stock.inventory.valuation'
    _description = 'Stock inventory valuation'
    def _get_total_valuation(self, cr, uid, ids, fields, arg, context=None):
        valuations = self.browse(cr, uid, ids, context=context)
        return {v.id: v.standard_price * v.product_qty for v in valuations}
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """Cancel the client action if there is no valuation to display"""
        if context is None:
            context = {}
        id = context.get('active_id', False)
        model = context.get('active_model')
        if id and model == 'stock.inventory':
            inventory = self.pool.get(model).browse(cr, uid, id, context=context)
            if not inventory.valuation_ids:
                raise osv.except_osv(_('No valuation'), _('No valuation was recorded for this Physical Inventory.'))
        return super(stock_inventory_valuation, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    _columns = {
        'name': fields.char('name', size=64, required=True, select=True),
        'inventory_id': fields.many2one('stock.inventory', 'Inventory',
                                        ondelete='cascade', readonly=True),
        'date': fields.related('inventory_id', 'date',
                                       relation='stock.inventory', type='date',
                                       readonly=True, store=True,
                                       string='Date'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='restrict',
                                      readonly=True),
        'category_id':  fields.related('product_id', 'categ_id',
                                       relation='product.category', type='many2one',
                                       readonly=True, store=True,
                                       string='Product Category'),
        'label_ids':  fields.related('product_id', 'label_ids',
                                       relation='product.label', type='many2many',
                                       readonly=True,
                                       string='Product Labels'),
        'product_qty': fields.float('Inventory Quantity',
                                    digits_compute=dp.get_precision('Product UoM'),
                                    readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
                                       readonly=True,
                                       help="unit of measure of product."),
        # XXX avg is pretty lame since it's not weighted by quantity
        'standard_price': fields.float('Unit Price',
                                       digits_compute=dp.get_precision('Product Price'),
                                       group_operator='min',
                                       help="Unit Cost Price of the Product at the date when the Inventory was confirmed."),
        # XXX should store that to get totals in the GUI
        'total_valuation': fields.function(_get_total_valuation, method=True,
            type="float", string='Total Valuation',
            digits_compute=dp.get_precision('Account'),
            store={'stock.inventory.valuation': (
                lambda self, cr, uid, ids, context=None: ids,
                ['standard_price'], 10), },
            readonly=True),
    }



class stock_inventory(osv.osv):
    """Add valuation to the physical inventory"""
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

    def action_cancel_inventory(self, cr, uid, ids, context=None):
        """ to delete records valuation on database.
        """
        siv_obj = self.pool.get('stock.inventory.valuation')
        for inv in self.browse(cr, uid, ids, context=context):
            siv_line_ids = siv_obj.search(cr, uid, [('inventory_id', '=', inv.id)])
            siv_obj.unlink(cr, uid, siv_line_ids, context=context)
        return super(stock_inventory, self).action_cancel_inventory(cr, uid, ids, context=context)
    
    # This is better done in copy_data() than copy() because copy_data() s called for related records too
    def copy_data(self, cr, uid, id, default=None, context=None):
        """Do not copy the product valuation when cloning inventories"""
        default = default and default.copy() or {}
        default['valuation_ids'] = []
        return super(stock_inventory, self).copy_data(cr, uid, id, default=default, context=context)

