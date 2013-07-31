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

from osv import osv, orm
from tools.translate import _

class StockInventoryCancelable(osv.osv):
    """Make inventories cancelable despite the constraint on stock move dates""" 
    _inherit = "stock.inventory"
    
    def action_cancel_inventary(self, cr, uid, ids, context=None):
        """Inject a context key to not block the deletion of stock moves"""
        if context is None:
            context = {}
        else:
            context = context.copy()
        context['ignore_inventories'] = ids
        return super(StockInventoryCancelable, self).action_cancel_inventary(
            cr, uid, ids, context=context)
StockInventoryCancelable()

class StockMoveConstraint(osv.osv):

    _inherit = 'stock.move'

    def _past_inventories(self, cr, uid, product_ids, prodlot_ids, location_ids, limit_date, context=None):
        """Search for inventories already finished after a given date"""
        # Search for inventory lines with the given location / prodlot / product
        if context is None:
            context = {}
        sil_obj = self.pool.get('stock.inventory.line')
        sil_ids = sil_obj.search(cr, uid, [('product_id', 'in', product_ids),
                                           ('prod_lot_id', 'in', prodlot_ids),
                                           ('location_id', 'in', location_ids),
                                           ('inventory_id', 'not in', context.get('ignore_inventories', []))],
                                 context=context)
        if not sil_ids:
            return []
        # Search for inventories dates after the move containing those lines
        inventory_ids = [i['inventory_id'][0]
                         for i in sil_obj.read(cr, uid,
                                               sil_ids, ['inventory_id'],
                                               context=context)]
        return self.pool.get('stock.inventory').search(
                cr, uid, [('id', 'in', inventory_ids),
                          ('state', '=', 'done'),
                          ('date', '>=', limit_date)], context=context)
    
    def create(self, cr, uid, vals, context=None):
        """Make sure the Stock Move being created doesn't make a finished inventory wrong"""
        # Take default values into account
        old_vals = vals
        vals = self.default_get(cr, uid,
                                  ['product_id', 'prodlot_id', 'location_id',
                                   'location_dest_id', 'date'],
                                  context=context)
        vals.update(old_vals)
        
        if vals.get('state') == 'done':
            inv_ids = self._past_inventories(cr, uid, [vals.get('product_id')],
                                             [vals.get('prodlot_id')],
                                             [vals.get('location_id'), vals.get('location_dest_id')],
                                             vals.get('date'), context=context)
            if inv_ids:
                # Make a message string with the names of the Inventories
                inventories = self.pool.get("stock.inventory").browse(cr, uid, inv_ids, context=context)
                msg = "\n".join([_("- %s (ID %d)") % (i.name, i.id)
                                 for i in inventories])
                raise orm.except_orm(
                    _('Wrong Stock Moves'),
                    _('The changes cannot be made because they conflict the following Stock Inventories:\n') + msg)
        return super(StockMoveConstraint, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        """Make sure the changes being made to the Stock Moves don't make a finished inventory wrong"""
        # XXX: the logic here is not 100% proven and may still allow some corner cases
        # The difficulty is that inventories can be changed by doing or undoing a move, changing it's date, product, prodlot etc.  
        inv_ids = []
        # Nothing to do if we change no value that can affect past inventories
        if ('state' not in vals
             and 'date' not in vals
             and 'locatation_id' not in vals
             and 'locatation_dest_id' not in vals
             and 'prodlot_id' not in vals
             and 'product_id' not in vals):
            return super(StockMoveConstraint, self).write(cr, uid, ids, vals, context=context)
        
        if not isinstance(ids, list):
            ids = [ids]
        for move in self.browse(cr, uid, ids, context=context):
            # Decide the limit date of the inventories that could be made wrong, depending on how the Stock Move is being changed
            new_state = vals.get('state', move.state)
            if move.state == 'done':
                if new_state == 'done':
                    # Get the earliest date from the new and the old date
                    limit_date = min(move.date, vals['date'])
                else:
                    limit_date = move.date
            else:
                if new_state == 'done':
                    limit_date = vals.get('date', move.date)
                else:
                    continue
            
            # Search for inventories conflicting the change
            inv_ids.extend(self._past_inventories(cr, uid,
                                      [vals.get('product_id'), move.product_id.id],
                                      [vals.get('prodlot_id'), move.prodlot_id.id],
                                      [vals.get('location_id'), move.location_id.id,
                                       vals.get('location_dest_id'), move.location_dest_id.id],
                                      limit_date, context=context))
        
        if inv_ids:
            # Make a message string with the names of the Inventories
            inventories = self.pool.get("stock.inventory").browse(cr, uid, inv_ids, context=context)
            msg = "\n".join([_("- %s (ID %d)") % (i.name, i.id)
                             for i in inventories])
            raise orm.except_orm(
                _('Wrong Stock Moves'),
                _('The changes cannot be made because they conflict the following Stock Inventories:\n') + msg)
        return super(StockMoveConstraint, self).write(cr, uid, ids, vals, context=context)
StockMoveConstraint()


class stock_inventory_line(osv.osv):
    """ Check if the new line will not be a duplicate line.
    Look for location_id, product_id and prod_lot_id.
    """
    _inherit = 'stock.inventory.line'

    def _check_duplicates_line(self, cr, uid, ids, context=None):
        """ Check for duplicates lines """
        message = ''
        for line in self.browse(cr, uid, ids, context=context):
            duplicates_count = self.search(cr, uid, [('location_id', '=', line.location_id.id),
                                                     ('product_id', '=', line.product_id.id),
                                                     ('prod_lot_id', '=', line.prod_lot_id.id),
                                                     ('inventory_id', '=', line.inventory_id.id)
                                               ], context=context, count=True)
            if duplicates_count > 1:
                message = '%s - %s - %s\n' % (line.location_id.name, line.prod_lot_id.name, line.product_id.name)

        if message:
            raise osv.except_osv(_('Warning : duplicates lines'),
                                 _('The following lines are duplicates and will be deleted :\n%s') % message)
        return True

    _constraints = [(_check_duplicates_line, 'Error: duplicates lines', ['location_id', 'product_id', 'prod_lot_id']), ]

stock_inventory_line()
