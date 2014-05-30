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

    def split(self, cr, uid, ids, split_qty, split_uos_qty, default=None,
              context=None):
        """Split Moves in two and return the new Stock Move ids.

        Splitting consists of making a new copy of the initial move and
        adjusting the quantities.
        The original move gets qty = initial qty - split_qty.
        The copy gets qty = split_qty.

        @param ids: List of ID of the original Stock Moves
        @param split_qty: Quantity to dispatch to new Stock Moves
        @param split_uos_qty: Quantity in UoS to dispatch to new Stock Moves
        @param default: Map of default values for the new Stock Moves
        @return: List of IDs of the new lines created
        """
        if default is None:
            default = {}
        if split_qty <= 0 or split_uos_qty <= 0:
            return []
        split_ids = []
        original_moves = self.read(
            cr, uid, ids, ['product_qty', 'product_uos_qty', 'state'])
        for move in original_moves:
            initial_qty = move['product_qty']
            initial_uos_qty = move['product_uos_qty']
            if initial_qty <= split_qty or initial_uos_qty <= split_uos_qty:
                # Special case where the quantity is actually increased
                # In this case we'll update the existing Stock Move instead
                self.write(
                    cr, uid, ids,
                    {
                        'product_qty': split_qty,
                        'product_uos_qty': split_uos_qty,
                    })
                continue
            # Adjust the quantity on the original move
            self.write(
                cr, uid, ids,
                {
                    'product_qty': initial_qty - split_qty,
                    'product_uos_qty': initial_uos_qty - split_uos_qty,
                })
            # Prepare the default values for the new Moves
            default.update({'product_qty': split_qty,
                            'product_uos_qty': split_uos_qty,
                            'state': move['state']})
            # XXX: copy() breaks traceability: is that OK?
            split_ids.append(
                self.copy(cr, uid, move['id'], default, context=context))
        return split_ids
