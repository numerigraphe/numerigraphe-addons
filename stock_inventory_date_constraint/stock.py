# encoding: utf-8
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


from osv import osv


class StockMoveConstraint(osv.osv):

    _inherit = 'stock.move'

    def date_before_inventory_constraint(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context):
            # All stock move havn't 'done' status are accepted
            if move.state != 'done':
                continue

            # search for last inventory date for tuple location / prodlot / product
            sil_obj = self.pool.get('stock.inventory.line')
            sil_ids = sil_obj.search(cr, uid, [('product_id', '=', move.product_id.id),
                                               ('prod_lot_id', '=', move.prodlot_id.id),
                                               ('location_id', 'in', [move.location_id.id, move.location_dest_id.id])], context=context)

            if not sil_ids:
                continue

            inventory_ids = sil_obj.read(cr, uid, sil_ids, ['inventory_id'], context=context)
            inventory_ids = [_id['inventory_id'][0] for _id in inventory_ids]

            # reading end date for each inventory
            inventory_ids = self.pool.get('stock.inventory').search(cr, uid, [('id', 'in', inventory_ids),
                                                                              ('state', '=', 'done'),
                                                                              ('date', '>', move.date)], context=context)

            if inventory_ids:
                return False
        return True

    _constraints = [(date_before_inventory_constraint, 'Error: The stock move is before the date of an inventory', ['state', 'date', 'location_id', 'prod_lot_id', 'product_id']), ]

StockMoveConstraint()
