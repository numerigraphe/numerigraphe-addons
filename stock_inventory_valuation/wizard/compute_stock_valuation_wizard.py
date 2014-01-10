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

from osv import osv, fields
from tools.translate import _
from datetime import datetime as dt
import tools


class compute_stock_valuation(osv.osv_memory):
    _name = "compute.stock.valuation"
    _description = "Compute stock valuation wizard"
    _auto = False

    _columns = {
                'name': fields.char('name', size=64),
                'location_id': fields.many2one('stock.location', 'Location', required=True),
                }

    def action_ok(self, cr, uid, ids, context=None):
        """ Check for name given for computation, or create a default one if not exist.
        Then call the computation module and open the result screen.
        """
        if context is None:
            context = {}

        stock_valuation = self.browse(cr, uid, ids[0], context=context)

        context_location = context.copy()
        context_location['location'] = stock_valuation.location_id.id
        if stock_valuation.name:
            context_location['name'] = stock_valuation.name
        else:
            context_location['name'] = _("Valuation of %s at %s" % (stock_valuation.location_id.name,
                                                                    dt.strftime(dt.now(), tools.DEFAULT_SERVER_DATE_FORMAT)))

        valuation_ids = self.pool.get('product.product').search_create_valuation(cr, uid, [('qty_available', '>', 0)], context=context_location)

        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock_inventory_valuation',
                                                                  'stock_inventory_valuation_tree_view')
        view_id = res and res[1] or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Valuations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': [view_id],
            'res_model': 'stock.inventory.valuation',
            'context': {'search_default_name': 1, 'search_default_category': 1, 'search_default_uom': 1},
            'domain': [('id', 'in', valuation_ids)],
        } or True

compute_stock_valuation()
