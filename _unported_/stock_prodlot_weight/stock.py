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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import decimal_precision as dp


class product_template(osv.osv):
    _inherit = 'product.template'

    def _get_weight_observed(self, cr, uid, ids, names, arg, context=None):
        """ Get the average weight of the lots in stock"""

        res = {}.fromkeys(ids, 0.0)
        # SUM(SP.QTY) cannot be zero because SP.QTY > 0
        cr.execute('''
                SELECT
                            SP.PRODUCT_ID,
                            SUM(SP.QTY * PL.WEIGHT_OBSERVED) / SUM(SP.QTY)  
                FROM        STOCK_REPORT_PRODLOTS SP 
                INNER JOIN  STOCK_PRODUCTION_LOT PL ON SP.PRODLOT_ID = PL.ID
                INNER JOIN  STOCK_LOCATION SL ON SP.LOCATION_ID = SL.ID
                WHERE       SP.PRODUCT_ID IN %s
                AND         SL.USAGE = 'internal'
                AND         SP.QTY > 0
                AND         PL.WEIGHT_OBSERVED > 0
                GROUP BY    SP.PRODUCT_ID''', (tuple(ids),)
        )
        res.update(dict(cr.fetchall()))
        return res

    def _search_weight_observed(self, cr, uid, obj, name, args, context=None):
        """Search for a product by average weight"""
        fieldname, operator, value = args[0]

        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise osv.except_osv(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, fieldname))
        # SUM(SP.QTY) cannot be zero because SP.QTY > 0
        cr.execute('''
                SELECT      SP.PRODUCT_ID
                FROM        STOCK_REPORT_PRODLOTS SP 
                INNER JOIN  STOCK_PRODUCTION_LOT PL ON SP.PRODLOT_ID = PL.ID
                INNER JOIN  STOCK_LOCATION SL ON SP.LOCATION_ID = SL.ID
                WHERE       SL.USAGE = 'internal'
                AND         SP.QTY > 0
                AND         PL.WEIGHT_OBSERVED > 0
                GROUP BY    SP.PRODUCT_ID
                HAVING      SUM(SP.QTY * PL.WEIGHT_OBSERVED) / SUM(SP.QTY) ''' + operator + " %s", (value, )
        )
        res = cr.fetchall()
        domain = [('id', 'in', map(lambda x: x[0], res))]
        return domain

    _columns = {
        'weight_observed': fields.function(
            _get_weight_observed, fnct_search=_search_weight_observed, method=True,
            digits_compute=dp.get_precision('Stock Weight'),
            type='float',
            string='Observed Weight',
            help="This is the average unit weight of the product in Kg, based on the "
                 "weights and quantities of the Production Lots currently "
                 "in stock."),
    }

    _defaults = {'weight_observed': 0.0}


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns = {
        'weight_observed': fields.float(
            'Observed Unit Weight',
            digits_compute=dp.get_precision('Stock Weight'),
            help="The Unit Weight observed for this Product in this Lot, in Kg."),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """Reset the weight on copied lots"""
        default = default and default.copy() or {}
        if 'weight_observed' not in default:
            default['weight_observed'] = 0.0
        return super(stock_production_lot, self).copy(cr, uid, id, default=default,
                                                      context=context)

