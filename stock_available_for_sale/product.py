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


# XXX :  Delete this function as soon as product._common can be imported.
def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r


class product_product(osv.osv):
    """Add the computation for the stock available for sale"""
    _inherit = 'product.product'

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """Compute the quantities available for sale and quantities in Quotations"""
        if not field_names:
            field_names = []
        
        # We need the virtual_available quantities in order to compute the quantities available for sale
        if 'available_for_sale' in field_names and not 'virtual_available' in field_names:
            field_names.append('virtual_available')
        
        # Compute the core quantities
        res = super(product_product, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        # Compute the quantities quoted/available to sale
        if 'quoted_qty' in field_names or 'available_for_sale' in field_names:
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
            uoms = map(lambda x: x[2], results)
            if context.get('uom', False):
                uoms.append(context['uom'])
            uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
            if uoms:
                uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o

            # compute available product from bom with n-1 available products
            # Beware of product uom of source and destination
            bom_obj = self.pool.get('mrp.bom')
            uom_obj = self.pool.get('product.uom')
            bom_available = {}
            for product, uom in product2uom.iteritems():
                bom = bom_obj._bom_find(cr, uid, product, uom)
                if bom:
                    bom_product_infos = bom_obj.read(cr, uid, [bom], ['child_complete_ids', 'product_qty'], context=context)[0]
                    bom_child_product_infos = bom_obj.read(cr, uid, bom_product_infos['child_complete_ids'], ['product_id', 'product_qty', 'product_uom'], context=context)
                    bom_child_product_ids = [p['product_id'][0] for p in bom_child_product_infos]
                    bom_child_product_qty = {bom_p['product_id'][0]: ({'product_qty': bom_p['product_qty'], 'product_uom': bom_p['product_uom'][0]}) for bom_p in bom_child_product_infos}
                    min_qty = 999999999999.0
                    for bom_product in self.browse(cr, uid, bom_child_product_ids, context=context):
                        # qty of stock product available with bom uom
                        qty_avail = uom_obj._compute_qty(cr, uid, bom_product.uom_id.id, bom_product.virtual_available, bom_child_product_qty[bom_product['id']].get('product_uom'))
                        # qty we can make with qty of available product
                        qty_avail = rounding((qty_avail / bom_child_product_qty[bom_product['id']].get('product_qty')) * bom_product_infos['product_qty'], bom_product.uom_id.rounding)
                        if qty_avail < min_qty:
                            min_qty = qty_avail
                    bom_available[product] = min_qty

            # Initialize the results
            for i in res.keys():
                if 'quoted_qty' in field_names:
                    res[i]['quoted_qty'] = 0.0
                if 'available_for_sale' in field_names:
                    res[i]['available_for_sale'] = res[i]['virtual_available']

            for (amount, prod_id, prod_uom) in results:
                # Convert the amount in the reporting UoM
                amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                        uoms_o[context.get('uom', False) or product2uom[prod_id]])

                if 'quoted_qty' in field_names:
                    res[prod_id]['quoted_qty'] -= amount
                if 'available_for_sale' in field_names:
                    res[prod_id]['available_for_sale'] -= amount

            for prod_id, qty_available in bom_available.iteritems():
                if prod_id in res:
                    res[prod_id]['available_for_sale'] += qty_available

        return res

    _columns = {
        'available_for_sale': fields.function(
            _product_available, method=True, multi='qty_available_for_sale',
            type='float', digits_compute=dp.get_precision('Product UoM'),
            string='Available for Sale',
            help="Stock for this Product that has not yet been included in any "
                 "Quotation (Draft Sale Order) (Computed as: Virtual Stock - "
                 "Quoted).\n"
                 "In a context with a single Shop, this includes the "
                 "Quotation processed at this Shop.\n"
                 "In a context with a single Warehouse, this includes "
                 "Quotation processed in any Shop using this Warehouse.\n"
                 "In a context with a single Stock Location, this includes "
                 "Quotation processed at any shop using any Warehouse using "
                 "this Location, or any of its children, as it's Stock "
                 "Location.\n"
                 "Otherwise, this includes every Quotation."),
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

#
