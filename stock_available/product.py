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
        """Dummy field. Must to be overridden by another module."""
        # Check the context
        if context is None:
            context = {}

        if field_names is None:
            field_names = []

        # We need the virtual_available quantities in order to compute the quantities available for sale
        if ('available_for_sale' in field_names or context.get('virtual_is_available_for_sale', False)) and not 'virtual_available' in field_names:
            field_names.append('virtual_available')

        # Compute the core quantities
        res = super(product_product, self)._product_available(
            cr, uid, ids, field_names=field_names, arg=arg, context=context)

        # Compute the quantities available for sale
        if ('available_for_sale' in field_names):
            # Initialize the fields before we actually compute the values
            for i in res.keys():
                res[i]['available_for_sale'] = res[i]['virtual_available']

        return res

    def __init__(self, pool, cr):
        """Use the new function to compute the quantity available.

        Depending on the context, we may change the value of qty_available,
        but this field is not defined here.
        So we must change the function that computes it.
        Doing it in __init__ is cleaner than copying and pasting
        the field definition in _columns and should be compatible
        with future/customized versions.
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
            help="Stock for this Product that can be safely proposed "
                 "for sale to Customers.\n"
                 "Computed as: Virtual Stock + Potential - Quoted)."),
    }
