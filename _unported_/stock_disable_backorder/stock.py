# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import netsvc
from openerp.osv import orm


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def test_complete(self, cr, uid, ids, context=None):
        """Tests whether all the moves are done."""
        # Find all the moves of all the selected pickings
        move_obj = self.pool['stock.move']
        move_ids = move_obj.search(cr, uid, [('picking_id', 'in', ids)],
                                   context=context)
        return all([move.state == 'done'
                    for move in move_obj.browse(cr, uid, move_ids,
                                                context=context)])


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def action_cancel(self, cr, uid, ids, context=None):
        """Trigger the picking workflow when canceling normal moves"""
        result = super(StockMove, self).action_cancel(
            cr, uid, ids, context=context)
        wf_service = netsvc.LocalService("workflow")
        for picking_id in set([m.picking_id.id
                               for m in self.browse(cr, uid, ids,
                                                    context=context)
                               if m.picking_id]):
            wf_service.trg_write(uid, 'stock.picking', picking_id, cr)
        return result
