# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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

import time

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class stock_inventory_valuation(osv.osv):
    """
    Record information about products (quantity, standard price) for future reference.
    
    The unit price can be manually adjusted by users, and the total value is recomputed and cached.
    Historically this was a feature for physical inventories but it's now more generic.
    """
    _name = 'stock.inventory.valuation'
    _description = 'Stock inventory valuation'
    
    def _get_total_valuation(self, cr, uid, ids, fields, arg, context=None):
        """Method for the function field 'total_valuation'"""
        valuations = self.browse(cr, uid, ids, context=context)
        return {v.id: v.standard_price * v.product_qty for v in valuations}
        
    _columns = {
        'name': fields.char('Title', size=64, required=True, select=True),
        'date': fields.datetime('Date', readonly=True, required=True),
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
        'product_qty': fields.float('Quantity',
                                    digits_compute=dp.get_precision('Product UoM'),
                                    readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure',
                                       readonly=True,
                                       help="unit of measure of product."),
        # XXX avg is pretty lame since it's not weighted by quantity
        'standard_price': fields.float('Unit Price',
                                       digits_compute=dp.get_precision('Product Price'),
                                       group_operator='min',
                                       help="Unit Cost Price of the Product at the date the valuation was recorded."),
        'total_valuation': fields.function(_get_total_valuation, method=True,
            type="float", string='Total Valuation',
            digits_compute=dp.get_precision('Account'),
            store={'stock.inventory.valuation': (
                lambda self, cr, uid, ids, context=None: ids,
                ['standard_price'], 10), },
            readonly=True),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

stock_inventory_valuation()
