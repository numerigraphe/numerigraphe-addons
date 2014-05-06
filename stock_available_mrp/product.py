# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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
from openerp.osv import orm, fields
import decimal_precision as dp


class product_product(orm.Model):
    """Add the computation for the stock available for sale"""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """Compute the potential quantities available for sale.
        """
        # Check the context
        if context is None:
            context = {}
        # Prepare an alternative context without 'uom', to avoid cross-category conversions when reading the available stock of components
        if 'uom' in context:
            context_wo_uom = context.copy()
            del context_wo_uom['uom']
        else:
            context_wo_uom = context

        if field_names is None:
            field_names = []

        # Compute the core quantities
        res = super(product_product, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        # Compute the quantities quoted/potential/available for sale
        if ('potential_qty' in field_names):
            # Compute the potential quantity from BoMs with components available
            bom_obj = self.pool['mrp.bom']
            to_uom = 'uom' in context and self.pool['product.uom'].browse(cr,
                uid, context['uom'], context=context)

            for product in self.browse(cr, uid, ids, context=context):
                # _bom_find() returns a single BoM id. We will not check any other BoM for this product
                # uom is not used by the function, but needed to call her.
                bom_id = bom_obj._bom_find(cr, uid, product.id,
                                           product.uom_id.id)
                if bom_id:
                    min_qty = self._compute_potential_qty_from_bom(cr,
                        uid, bom_id, to_uom or product.uom_id,
                        context=context)

                    res[product.id]['potential_qty'] += min_qty
                    if ('available_for_sale' in field_names):
                        res[product.id]['available_for_sale'] += min_qty

        return res

    def _compute_potential_qty_from_bom(self, cr, uid, bom_id, to_uom, context):
        """ Compute the potential quantity from BoMs with components available
        """
        bom_obj = self.pool['mrp.bom']
        uom_obj = self.pool['product.uom']
        if 'uom' in context:
            context_wo_uom = context.copy()
            del context_wo_uom['uom']
        else:
            context_wo_uom = context
        min_qty = False
        # Browse ignoring the initial context's UoM to avoid cross-category conversions
        final_product = bom_obj.browse(cr,
            uid, [bom_id], context=context_wo_uom)[0]

        # store id of final product uom

        for component in final_product.bom_lines:
            # qty available in BOM line's UoM
            # XXX use context['uom'] instead?
            stock_component_qty = uom_obj._compute_qty_obj(cr, uid,
                component.product_id.uom_id,
                component.product_id.virtual_available,
                component.product_uom)
            # qty we can produce with this component, in the BoM's UoM
            recipe_uom_qty = (stock_component_qty // component.product_qty) * final_product.product_qty
            # Convert back to the reporting default UoM
            stock_product_uom_qty = uom_obj._compute_qty_obj(cr,
                uid, final_product.product_uom, recipe_uom_qty,
                 to_uom)
            if min_qty is False:
                min_qty = stock_product_uom_qty
            elif stock_product_uom_qty < min_qty:
                min_qty = stock_product_uom_qty
        if min_qty < 0.0:
            min_qty = 0.0
        return min_qty

    _columns = {
        'potential_qty': fields.function(
            _product_available, method=True, multi='qty_available_for_sale',
            type='float', digits_compute=dp.get_precision('Product UoM'),
            string='Potential',
            help="Quantity of this Product that could be produced using "
                 "the materials already at hand, following a single level"
                 "of the Bills of Materials."),
    }
