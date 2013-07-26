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

from osv import fields, osv

class stock_location_product(osv.osv_memory):
    _name = 'stock.location.product'
    _inherit = 'stock.location.product'
    _columns = {
        'partner_id': fields.many2one('res.partner',
                                      "Display Partner's references"),
    }
    
    def action_open_window(self, cr, uid, ids, context=None):
        """Add the selected partner to the context"""
        # Call the standard method
        result = super(stock_location_product, self).action_open_window(
                                                cr, uid, ids, context=context)
        # Make sure we have proper dictionaries
        if result is None:
            result = {}
        if result.get('context') is None:
            result['context'] = {}
        # Get the partner from the wizard and add it to the context
        location_product = self.read(cr, uid, ids, ['partner_id'])
        if location_product:
            # XXX in trunk , change to  ... = location_product[0]['partner_id'][0]
            result['context']['partner_id'] = location_product[0]['partner_id']
        
        return result
            
stock_location_product()


