# -*- encoding: utf-8 -*-
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

from osv import osv, fields
from tools.translate import _

class stock_production_lot(osv.osv):

    _inherit = 'stock.production.lot'

    _columns = {
        'locked': fields.boolean('Validation Wait', help="No move can be created if checked"),
    }

    _defaults = {
         'locked': lambda *a: False,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
        Inherit this methode to do like active field, we want select only the unlocked lot
        In the context the value locked_test can be let search the unlocked and the locked lot
        """
        if context is None:
            context = {}
        # make a copy of args because it is a list, we dont want the modification of args be returned
        if args:
            new_args = list(args)
        else:
            new_args = []
        if context.get('locked_test', True):
            lock_in_args = False
            for arg in args:
                if arg[0] == 'locked':
                    lock_in_args = True
            if not lock_in_args:
                new_args.append(('locked', '=', False))
        return super(stock_production_lot, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)

    def lock(self, cr, uid, id, context=None):
        self.write(cr, uid, [id], {'locked': True}, context=context)

    def unlock(self, cr, uid, id, context=None):
        self.write(cr, uid, [id], {'locked': False}, context=context)

stock_production_lot()

class stock_move(osv.osv):

    _inherit = 'stock.move'

    def _check_prodlot(self, cr, uid, ids, context=None):
        """
        for each move check if the production lot is unlock
        if the lot is lock raise
        """
        if context is None:
            context = {}
        if not context.get('locked_move', True):
            return True
        message = ""
        for move in self.browse(cr, uid, ids, context=context):
            if move.prodlot_id and move.prodlot_id.locked:
                message += _('the move (%d, %s) has got a locked production lot (%d, %s)\n') % (move.id, move.name, move.prodlot_id.id, move.prodlot_id.name)
        if message:
            raise osv.except_osv(_('Forbiden move'), _('You can\'t move the locked production lot\n\n') + message)
        return True

    def create(self, cr, uid, values, context=None):
        """
        Check if the lot can be move
        """
        id = super(stock_move, self).create(cr, uid, values, context=context)
        self._check_prodlot(cr, uid, [id], context=context)
        return id

    def write(self, cr, uid, ids, values, context=None):
        """
        Inherit this method to check if the lot can be move
        """
        product_product_obj = self.pool.get('product.product')
        product_uom_obj = self.pool.get('product.uom')
        if not isinstance(ids, list):
            ids = [ids]
        for id in ids:
            vals = values.copy()
            if not super(stock_move, self).write(cr, uid, [id], vals, context=context):
                return False
        self._check_prodlot(cr, uid, ids, context=context)
        return True

stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
