# -*- encoding: utf-8 -*-
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

from osv import fields, osv
import decimal_precision as dp

class product_template(osv.osv):
    _inherit = 'product.template'

    def _get_weight_average(self, cr, uid, ids, names, arg, context=None):
        """ Get a average weight of the lot numbers where the stock qty greater 0"""
        
        if context is None:
            context = {}

        res = {}.fromkeys(ids, 0.0)
        cr.execute('''
                SELECT
                            SP.PRODUCT_ID,
                            SUM(SP.QTY * PL.UNIT_WEIGHT_AVERAGE) / SUM(SP.QTY)  
                FROM        STOCK_REPORT_PRODLOTS SP 
                INNER JOIN  STOCK_PRODUCTION_LOT PL ON SP.PRODLOT_ID = PL.ID
                INNER JOIN  STOCK_LOCATION SL ON SP.LOCATION_ID = SL.ID
                WHERE       SP.PRODUCT_ID IN %s
                AND         SL.USAGE = 'internal'
                AND         SP.QTY > 0
                GROUP BY    SP.PRODUCT_ID
                HAVING      SUM(SP.QTY) != 0 ''', (tuple(ids),)
                
        )
        
        res.update(dict(cr.fetchall()))        
        return res
    
    def _get_weight_average_search(self, cr, uid, obj, name, args, context=None):
        """ Get a average weight of the lot numbers where the stock qty greater 0"""
        
        if context is None:
            context = {}

        cr.execute('''
                SELECT
                            SP.PRODUCT_ID,
                            CASE 
                            WHEN SUM(SP.QTY) > 0 THEN
                                SUM(SP.QTY * PL.UNIT_WEIGHT_AVERAGE) / SUM(SP.QTY)
                            ELSE
                                0
                            END         
                FROM        STOCK_REPORT_PRODLOTS SP 
                INNER JOIN  STOCK_PRODUCTION_LOT PL ON SP.PRODLOT_ID = PL.ID
                INNER JOIN  STOCK_LOCATION SL ON SP.LOCATION_ID = SL.ID
                WHERE       SL.USAGE = 'internal'
                AND         SP.QTY > 0
                GROUP BY    SP.PRODUCT_ID
                HAVING      CASE 
                            WHEN SUM(SP.QTY) > 0 THEN
                                SUM(SP.QTY * PL.UNIT_WEIGHT_AVERAGE) / SUM(SP.QTY)
                            ELSE
                                0
                            END ''' + str(args[0][1]) + str(args[0][2])
        )
        
        res = cr.fetchall()
        domain = [('id', 'in', map(lambda x: x[0], res))]
        return domain
    
    _columns = {
        'weight_average': fields.function(_get_weight_average,
                                          fnct_search=_get_weight_average_search,
                                          method=True,
                                          # XXX use digits_compute=dp.get_precision('Stock Weight')
                                          type='float', digits=(16, 5),
                                          string='Weight Average',
                                          help='Get a average weight of the lot numbers not empty in Kg'),
    }
product_template()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    
    _columns = {
        'unit_weight_average': fields.float(
             # XXX use digits_compute=dp.get_precision('Stock Weight')
            'Unit Average weight', digits=(16, 4), help="The unit average weight in Kg."),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        """Reset the weight on copied lots"""
        if default is None:
            default = {}
        if 'weight_average' not in default:
            default['weight_average'] = 0.0
        return super(stock_production_lot, self).copy(cr, uid, id, default=default,
                                                      context=context)
stock_production_lot()
