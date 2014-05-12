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
        """Compute the quantities in Quotations.
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
        if ('quoted_qty' in field_names):
            date_str, date_args = self._get_dates(cr, uid, ids, context=context)

            # Limit the search to some shops according to the context
            shop_str, shop_args = self._get_shops(cr, uid, ids, context=context)

            # Query the total by Product and UoM
            cr.execute(
                "SELECT sum(product_uom_qty), product_id, product_uom "
                "FROM sale_order_line "
                "INNER JOIN sale_order ON "
                "(sale_order_line.order_id = sale_order.id) "
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
            uom_obj = self.pool['product.uom']
            uoms = map(lambda stock_product_uom_qty: stock_product_uom_qty[2],
                       results)
            if context.get('uom', False):
                uoms.append(context['uom'])
            uoms = filter(lambda stock_product_uom_qty: stock_product_uom_qty not in uoms_o.keys(), uoms)
            if uoms:
                uoms = uom_obj.browse(cr, uid, list(set(uoms)),
                    context=context)
            for o in uoms:
                uoms_o[o.id] = o

            # Compute the quoted quantity
            for (amount, prod_id, prod_uom) in results:
                # Convert the amount in the reporting UoM
                amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom],
                    amount, uoms_o[context.get('uom', False) or product2uom[prod_id]])
                res[prod_id]['quoted_qty'] -= amount
                if ('available_for_sale' in field_names):
                    res[prod_id]['available_for_sale'] -= amount
        return res

    def _get_shops(self, cr, uid, ids, context=None):
        """ """
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
                child_location_ids = self.pool['stock.location'].search(cr,
                    uid, [('location_id', 'child_of', location_ids)])
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

        # If we are in a single Shop context, only count the quotations from this shop
        if context.get('shop', False):
            shop_ids.append(context['shop'])
        # Build the SQL to restrict to the selected shops
        shop_str = ''
        if shop_ids:
            shop_str = 'AND sale_order.shop_id IN %s'

        if shop_ids:
            shop_ids = (tuple(shop_ids),)
        else:
            shop_ids = ()
        return shop_str, shop_ids

    def _get_dates(self, cr, uid, ids, context=None):
        """ Return string with from and to date SQL criteria """
        # If we are in a context with dates, only consider the quotations to be delivered at these dates
        # If no delivery date was entered, use the order date instead
        if not context:
            return '', ()

        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_str = ''
        date_args = []
        if from_date:
            date_str = "AND COALESCE(sale_order.requested_date, sale_order.date_order) >= %s "
            date_args.append(from_date)
        if to_date:
            date_str += "AND COALESCE(sale_order.requested_date, sale_order.date_order) <= %s "
            date_args.append(to_date)

        if date_args:
            date_args = (tuple(date_args),)
        else:
            date_args = ()
        return date_str, date_args

    _columns = {
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
