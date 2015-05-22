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

from openerp import models, fields
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight_observed = fields.Float(
            compute='_get_weight_observed', 
            search='_search_weight_observed',
            digits=dp.get_precision('Stock Weight'),
            string='Observed Weight',
            help="This is the average unit weight of the product in Kg, based on the "
                 "weights and quantities of the Quant.")

    
    def _get_weight_observed(self):
        """Get the average weight of the lots in stock""" 
        self.env.cr.execute("""
            SELECT      PRODUCT_ID, 
                        SUM(SQ.QTY * SQ.WEIGHT_OBSERVED) / SUM(SQ.qty)
            FROM        STOCK_QUANT SQ
            INNER JOIN  STOCK_LOCATION SL ON SQ.LOCATION_ID = SL.ID
            WHERE       SQ.PRODUCT_ID IN %s
            AND         SL.USAGE = 'internal'
            AND         SQ.QTY > 0
            AND         SQ.WEIGHT_OBSERVED > 0
            GROUP BY    PRODUCT_ID""", (tuple(self.ids),))
        r = dict( self.env.cr.fetchall())
        for record in self:
            record.weight_observed = r.get(record.id, 0.0)
            
            
    def _search_weight_observed(self, operator, value):
        """Search for a product by average weight"""
        # Sanitize input to protect from SQL injection
        if operator not in ('=', '!=', '<>', '<=', '<', '>', '>=', 'in', 'not in'):
            raise models.except_orm(
               _('Invalid operator!'),
               _("The operator '%s' cannot be used to filter the field '%s'.") % (operator, self._name))
        self.env.cr.execute('''
                SELECT      SQ.PRODUCT_ID
                FROM        STOCK_QUANT SQ 
                INNER JOIN  STOCK_LOCATION SL ON SQ.LOCATION_ID = SL.ID
                WHERE       SL.USAGE = 'internal'
                AND         SQ.QTY > 0
                AND         SQ.WEIGHT_OBSERVED > 0
                GROUP BY    SQ.PRODUCT_ID
                HAVING      SUM(SQ.QTY * SQ.WEIGHT_OBSERVED) / SUM(SQ.QTY) ''' + operator + " %s", (value, )
        )
        res = self.env.cr.fetchall()
        domain = [('id', 'in', map(lambda x: x[0], res))]
        return domain


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    weight_observed = fields.Float(
        'Observed Unit Weight',
        digits=dp.get_precision('Stock Weight'),
        help="The Unit Weight observed for this Product in this Lot, in Kg.")
