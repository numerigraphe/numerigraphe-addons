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

from osv import osv, fields
import decimal_precision as dp


class product_product(osv.osv):
    """Add the computation for the stock available for sale"""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """Compute the quantities available for sale and quantities in Quotations
        
        @param context: 'virtual_is_available_for_sale': if this key is True, then
                        the value of virtual_available will be replaced with that of 
                        available_for_sale. This lets you change the basis for some
                        computations without changing too much business code.
                        See sale_stock.py for an example.
                        'uom': id of the UoM the quantity will be reported in
        """
        # Check the context
        if context is None:
            context = {}
        # Does the context require us to replace the virtual available quantity with the quantity available for sale?
        replace_virtual = context.get('virtual_is_available_for_sale', False)
        if replace_virtual:
            # We still want the virtual stock to mean virtual stock *inside* this method (otherwise the results would be wrong, browse() would recurse endlessly)
            context = context.copy()
            del context['virtual_is_available_for_sale']
        # Prepare an alternative context without 'uom', to avoid cross-category conversions when reading the available stock of components
        if 'uom' in context:
            context_wo_uom = context.copy()
            del context_wo_uom['uom']
        else:
            context_wo_uom = context
        
        if field_names is None:
            field_names = []
        # We need the virtual_available quantities in order to compute the quantities available for sale
        if ('available_for_sale' in field_names or replace_virtual) and not 'virtual_available' in field_names:
            field_names.append('virtual_available')
        
        # Compute the core quantities
        res = super(product_product, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)
        
        # Compute the quantities quoted/potential/available for sale
        if ('quoted_qty' in field_names
            or 'available_for_sale' in field_names
            or 'potential_qty' in field_names
            or replace_virtual):
            # If we are in a context with dates, only consider the quotations to be delivered at these dates
            # If no delivery date was entered, use the order date instead
            from_date = context.get('from_date', False)
            to_date = context.get('to_date', False)
            date_str = ''
            date_args = ()
            if from_date and to_date:
                date_str = "AND COALESCE(sale_order.requested_date, sale_order.date_order) >= %s AND COALESCE(sale_order.requested_date, sale_order.date_order) <= %s "
                date_args = (from_date, to_date)
            elif from_date:
                date_str = "AND COALESCE(sale_order.requested_date, sale_order.date_order) >= %s "
                date_args = (from_date,)
            elif to_date:
                date_str = "AND COALESCE(sale_order.requested_date, sale_order.date_order) <= %s "
                date_args = (to_date,)

            # Limit the search to some shops according to the context
            shop_ids = []
            # Account for one or several locations in the context
            # Take any shop using any warehouse that has these locations as stock location
            if context.get('location', False):
                # Either a single or multiple locations can be in the context 
                if not isinstance(context['location'], list):
                    location_ids = [context['location']]
                else:
                    location_ids = context['location']
                # Add the children locations
                if context.get('compute_child', True):
                    child_location_ids = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', location_ids)])
                    location_ids = child_location_ids or location_ids
                # Get the corresponding Shops
                cr.execute("SELECT id FROM sale_shop "
                           "WHERE warehouse_id IN ("
                                "SELECT id "
                                "FROM stock_warehouse "
                                "WHERE lot_stock_id IN %s)",
                            (tuple(location_ids),))
                res_location = cr.fetchone()
                if res_location:
                    shop_ids.append(res_location)
                else:
                    # Give up if we found no shop
                    return res
            # Account for a warehouse in the context
            # Take any draft order in any shop using this warehouse
            if context.get('warehouse', False):
                cr.execute("SELECT id " 
                           "FROM sale_shop "
                           "WHERE warehouse_id = %s",
                           (int(context['warehouse']),))
                res_wh = cr.fetchone()
                if res_wh:
                    shop_ids.append(res_wh)
                else:
                    # Give up if we found no warehouse
                    return res
            # If we are in a single Shop context, only count the quotations from this shop
            if context.get('shop', False):
                shop_ids.append(context['shop'])
            # Build the SQL to restrict to the selected shops
            shop_str = ''
            shop_args = ()
            if shop_ids:
                shop_str = 'AND sale_order.shop_id IN %s'
                shop_args = (tuple(shop_ids),)
            
            # Query the total by Product and UoM
            cr.execute(
                "SELECT sum(product_uom_qty), product_id, product_uom "
                "FROM sale_order_line "
                "    INNER JOIN sale_order ON (sale_order_line.order_id = sale_order.id)" 
                "WHERE product_id in %s "
                "      AND sale_order_line.state = 'draft' "
                       + date_str + shop_str + 
                "GROUP BY sale_order_line.product_id, "
                "         product_uom",
                (tuple(ids),) + date_args + shop_args)
            results = cr.fetchall()
            
            # Get the UoM resources we'll need for conversion
            # UoMs from the products
            uoms_o = {}
            product2uom = {}
            for product in self.browse(cr, uid, ids, context=context):
                product2uom[product.id] = product.uom_id.id
                uoms_o[product.uom_id.id] = product.uom_id
            # UoM from the results and the context
            uom_obj = self.pool.get('product.uom')
            uoms = map(lambda stock_product_uom_qty: stock_product_uom_qty[2], results)
            if context.get('uom', False):
                uoms.append(context['uom'])
            uoms = filter(lambda stock_product_uom_qty: stock_product_uom_qty not in uoms_o.keys(), uoms)
            if uoms:
                uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
            
            # Initialize the fields before we actually compute the values
            for i in res.keys():
                if 'quoted_qty' in field_names:
                    res[i]['quoted_qty'] = 0.0
                if 'potential_qty' in field_names:
                    res[i]['potential_qty'] = 0.0
                if 'available_for_sale' in field_names or replace_virtual:
                    res[i]['available_for_sale'] = res[i]['virtual_available']
            
            # Compute the quoted quantity
            for (amount, prod_id, prod_uom) in results:
                # Convert the amount in the reporting UoM
                amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                        uoms_o[context.get('uom', False) or product2uom[prod_id]])
                if 'quoted_qty' in field_names:
                    res[prod_id]['quoted_qty'] -= amount
                if 'available_for_sale' in field_names or replace_virtual:
                    res[prod_id]['available_for_sale'] -= amount
            
            # Compute the potential quantity from BoMs with components available
            bom_obj = self.pool.get('mrp.bom')
            bom_available = {}
            for product_id, uom in product2uom.iteritems():
                # _bom_find() returns a single BoM id. We will not check any other BoM for this product
                # uom is not used by the function, but needed to call her.
                bom_id = bom_obj._bom_find(cr, uid, product_id, uom)
                if bom_id:
                    min_qty = False
                    # Browse ignoring the initial context's UoM to avoid cross-category conversions
                    final_product = bom_obj.browse(cr, uid, [bom_id], context=context_wo_uom)[0]
                    for component in final_product.bom_lines:
                        # qty available in BOM line's UoM
                        # XXX use context['uom'] instead?
                        stock_component_qty = uom_obj._compute_qty_obj(cr, uid,
                            component.product_id.uom_id, component.product_id.virtual_available, component.product_uom)
                        # qty we can produce with this component, in the BoM's UoM
                        recipe_uom_qty = (stock_component_qty / component.product_qty) * final_product.product_qty
                        # Convert back to the reporting default UoM
                        stock_product_uom_qty = uom_obj._compute_qty_obj(cr, uid,
                             final_product.product_uom, recipe_uom_qty,
                             context.get('uom', False) and uoms_o[context['uom']] or final_product.product_id.uom_id)
                        if min_qty is False:
                            min_qty = stock_product_uom_qty
                        elif stock_product_uom_qty < min_qty:
                            min_qty = stock_product_uom_qty
                    if 'available_for_sale' in field_names or replace_virtual:
                        res[product_id]['available_for_sale'] += min_qty
                    if 'potential_qty' in field_names:
                        res[product_id]['potential_qty'] += min_qty
            
            # If required by the context, replace the virtual available quantity with the quantity available for sale
            if replace_virtual:
                for i in res.keys():
                    res[i]['virtual_available'] = res[i]['available_for_sale']
        return res
 
    def __init__(self, pool, cr):
        """Use the new function to compute the quantity available.
        
        Depending on the context, we may change the value of qty_available, but this field is not defined here.
        So we must change the function that computes it. Doing it in __init__ is cleaner than copying and pasting
        the field definition in _columns and should be compatible with future/customized versions.
        """
        s = super(product_product, self)
        res = s.__init__(pool, cr)
        self._columns['virtual_available']._fnct = self._columns['available_for_sale']._fnct
        return res
    
    _columns = {
        'available_for_sale': fields.function(
            _product_available, method=True, multi='qty_available_for_sale',
            type='float', digits_compute=dp.get_precision('Product UoM'),
            string='Available for Sale',
            help="Stock for this Product that can be safely proposed for sale to Customers. \n"
                "Computed as: Virtual Stock + Potential - Quoted)."),
        'potential_qty': fields.function(
            _product_available, method=True, multi='qty_available_for_sale',
            type='float', digits_compute=dp.get_precision('Product UoM'),
            string='Potential',
            help="Quantity of this Product that could be produced using "
                 "the materials already at hand, following a single level of the Bills of Materials."),
        'quoted_qty': fields.function(
            _product_available, method=True, multi='qty_available_for_sale',
            type='float', digits_compute=dp.get_precision('Product UoM'),
            string='Quoted',
            help="Total quantity of this Product that have been included in "
                 "Quotations (Draft Sale Orders).\n"
                 "In a context with a single Shop, this includes the "
                 "Quotation processed at this Shop.\n"
                 "In a context with a single Warehouse, this includes "
                 "Quotation processed in any Shop using this Warehouse.\n"
                 "In a context with a single Stock Location, this includes "
                 "Quotation processed at any shop using any Warehouse using "
                 "this Location, or any of its children, as it's Stock "
                 "Location.\n"
                 "Otherwise, this includes every Quotation."),
    }
product_product()

